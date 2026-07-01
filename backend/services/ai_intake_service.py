"""
AI Intake Summary

Produces the structured hand-off a lawyer receives for a new client: a plain
summary of the matter and suggested next steps. Uses OpenAI when configured,
otherwise a rule-based fallback. It summarises intake — it is not legal advice.
"""
from __future__ import annotations

import json
import os

DISCLAIMER = "Intake summary for the assigned lawyer. Not legal advice."


def _rule_based(intake: dict, triage: dict) -> dict:
    name = intake.get("client_name", "Client")
    area = triage.get("practice_area", "General")
    urgency = triage.get("urgency", "medium")
    quality = triage.get("lead_quality", "warm")

    steps = [
        f"Review the {area} matter and confirm scope at consultation.",
        "Verify identity and run the conflict check before engagement.",
    ]
    if urgency == "high":
        steps.insert(0, "Prioritise — client flagged this as urgent.")

    summary = (
        f"{name} submitted a {area} matter (urgency: {urgency}, lead: {quality}). "
        f"Requested help: {intake.get('requested_help', 'consultation')}. "
        f"Description: {intake.get('description', '')}"
    )
    return {
        "summary": summary,
        "suggested_next_steps": steps,
        "generated_with": "rule-based-fallback",
        "disclaimer": DISCLAIMER,
    }


def _openai(intake: dict, triage: dict) -> dict:
    from openai import OpenAI

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    prompt = (
        "You are a legal intake assistant (not a lawyer). Summarise this client "
        "intake for the assigned lawyer. Return JSON with 'summary' (3-4 sentences) "
        "and 'suggested_next_steps' (array). Do not give legal advice.\n\n"
        f"{json.dumps({'intake': intake, 'triage': triage})}"
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.4,
    )
    data = json.loads(resp.choices[0].message.content)
    data["generated_with"] = "openai"
    data["disclaimer"] = DISCLAIMER
    return data


def summarize_for_lawyer(intake: dict, triage: dict) -> dict:
    if os.getenv("OPENAI_API_KEY"):
        try:
            return _openai(intake, triage)
        except Exception:
            return _rule_based(intake, triage)
    return _rule_based(intake, triage)
