"""
Conversation Engine (AI Intake Agent)

A finite-state intake dialog: it greets the caller, collects their details and
matter, answers general questions from the knowledge base (RAG), then offers to
book a consultation and hands a structured summary to the firm.

It never gives legal advice — only general information and intake handling.
"""
from __future__ import annotations

from . import rag_service, triage_service

DISCLAIMER = "I can share general information and set up a consultation, but I can't give legal advice."

# Ordered steps of the intake dialog.
STEPS = ["greet", "name", "contact", "matter", "urgency", "info", "offer_appointment", "done"]

PROMPTS = {
    "name": "Thanks for contacting the firm. What is your full name?",
    "contact": "Thank you. What's the best email or phone number to reach you?",
    "matter": "Please briefly describe the legal matter you need help with.",
    "urgency": "How urgent is this — low, medium or high?",
}


def start() -> dict:
    return {
        "state": {"step": "name", "data": {}},
        "message": f"Hello! {DISCLAIMER} " + PROMPTS["name"],
    }


def advance(state: dict, user_message: str, knowledge_base: list) -> dict:
    step = state.get("step", "name")
    data = dict(state.get("data", {}))
    msg = (user_message or "").strip()
    reply = ""
    next_step = step

    if step == "name":
        data["client_name"] = msg
        next_step = "contact"
        reply = PROMPTS["contact"]

    elif step == "contact":
        if "@" in msg:
            data["contact_email"] = msg
        else:
            data["contact_phone"] = msg
        next_step = "matter"
        reply = PROMPTS["matter"]

    elif step == "matter":
        data["description"] = msg
        area = triage_service.classify_practice_area(msg)
        data["practice_area"] = area
        next_step = "urgency"
        reply = f"Understood — this looks like a {area} matter. {PROMPTS['urgency']}"

    elif step == "urgency":
        data["urgency"] = msg.lower() if msg.lower() in {"low", "medium", "high"} else "medium"
        # Offer relevant general info via retrieval.
        rag = rag_service.retrieve(data.get("description", ""), knowledge_base, k=1)
        next_step = "offer_appointment"
        reply = (
            f"{rag['answer']} ({rag['disclaimer']}) "
            "Would you like me to schedule a consultation with a lawyer? (yes/no)"
        )

    elif step == "offer_appointment":
        if msg.lower().startswith("y"):
            data["wants_appointment"] = True
            reply = "Great — I'll pass your details to the right lawyer and we'll confirm a time."
        else:
            data["wants_appointment"] = False
            reply = "No problem. Your details are saved; contact us anytime to proceed."
        next_step = "done"

    else:
        reply = "Your intake is complete. Thank you."
        next_step = "done"

    return {
        "state": {"step": next_step, "data": data},
        "message": reply,
        "complete": next_step == "done",
    }
