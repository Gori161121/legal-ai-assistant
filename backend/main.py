"""
Legal Intake Platform — API + server-rendered portal.

An AI intake agent (conversational), matter triage, lawyer routing, consultation
scheduling, a knowledge-base retrieval (RAG) endpoint, plus server-rendered
lawyer dashboard and client portal pages (Jinja2).

The assistant handles intake and shares general information only — it does not
give legal advice.
"""
from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend.data_loader import load_data, load_knowledge_base
from backend.services import (
    ai_intake_service,
    analytics_service,
    case_service,
    conflict_service,
    conversation_service,
    document_service,
    rag_service,
    routing_service,
    scheduling_service,
    triage_service,
)

TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))

app = FastAPI(
    title="Legal Intake Platform API",
    description=(
        "AI intake agent, matter triage, lawyer routing, consultation scheduling, "
        "knowledge-base retrieval and a client portal for a law firm. "
        "Handles intake and general information only — not legal advice."
    ),
    version="0.2.0",
)

# In-memory conversation sessions (a cache/DB would back this in production).
SESSIONS: dict[str, dict] = {}


def _data() -> dict:
    return load_data()


class ChatIn(BaseModel):
    session_id: str | None = None
    message: str | None = None


class ConflictIn(BaseModel):
    client_name: str
    description: str = ""


# --- Meta -----------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# --- Raw data -------------------------------------------------------------

@app.get("/lawyers")
def lawyers():
    return _data()["lawyers"]


@app.get("/intakes")
def intakes():
    return _data()["intakes"]


@app.get("/appointments")
def appointments():
    return _data()["appointments"]


# --- AI intake conversation ----------------------------------------------

@app.post("/intake/chat")
def intake_chat(payload: ChatIn):
    kb = load_knowledge_base()

    if not payload.session_id or payload.session_id not in SESSIONS:
        session_id = payload.session_id or str(uuid.uuid4())
        started = conversation_service.start()
        SESSIONS[session_id] = started["state"]
        return {"session_id": session_id, "message": started["message"], "complete": False}

    session_id = payload.session_id
    result = conversation_service.advance(SESSIONS[session_id], payload.message or "", kb)
    SESSIONS[session_id] = result["state"]
    return {
        "session_id": session_id,
        "message": result["message"],
        "complete": result["complete"],
        "collected": result["state"]["data"] if result["complete"] else None,
    }


# --- Intelligence ---------------------------------------------------------

@app.get("/intake/{intake_id}/triage")
def triage(intake_id: int):
    intake = next((i for i in _data()["intakes"] if i["id"] == intake_id), None)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    return triage_service.triage_intake(intake)


@app.get("/intake/{intake_id}/summary")
def intake_summary(intake_id: int):
    intake = next((i for i in _data()["intakes"] if i["id"] == intake_id), None)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    return ai_intake_service.summarize_for_lawyer(intake, triage_service.triage_intake(intake))


@app.get("/intake/{intake_id}/documents")
def intake_documents(intake_id: int):
    return document_service.document_status(intake_id, _data()["documents"])


@app.get("/intake/{intake_id}/routing")
def intake_routing(intake_id: int):
    data = _data()
    intake = next((i for i in data["intakes"] if i["id"] == intake_id), None)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    area = triage_service.classify_practice_area(intake.get("description", ""))
    workload = routing_service.current_workload(data["intakes"])
    return routing_service.suggest_lawyer(area, data["lawyers"], workload)


@app.get("/intake/{intake_id}/slots")
def intake_slots(intake_id: int):
    data = _data()
    intake = next((i for i in data["intakes"] if i["id"] == intake_id), None)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found")
    lawyer_id = intake.get("assigned_lawyer_id") or data["lawyers"][0]["id"]
    return {"intake_id": intake_id, "slots": scheduling_service.propose_slots(lawyer_id, data["appointments"])}


@app.post("/conflict-check")
def conflict_check(payload: ConflictIn):
    return conflict_service.check_conflict(payload.client_name, payload.description, _data()["intakes"])


@app.get("/knowledge/search")
def knowledge_search(q: str):
    return rag_service.retrieve(q, load_knowledge_base())


# --- Firm views (JSON) ----------------------------------------------------

@app.get("/pipeline")
def pipeline():
    return case_service.pipeline_overview(_data()["intakes"])


@app.get("/stale")
def stale():
    return case_service.stale_intakes(_data()["intakes"])


@app.get("/analytics")
def analytics():
    return analytics_service.firm_analytics(_data()["intakes"])


# --- Server-rendered pages (Jinja2) --------------------------------------

@app.get("/", response_class=HTMLResponse)
def landing(request: Request):
    return TEMPLATES.TemplateResponse("landing.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    data = _data()
    rows = []
    for i in data["intakes"]:
        t = triage_service.triage_intake(i)
        rows.append({**i, "practice_area": t["practice_area"],
                     "lead_score": t["lead_score"], "lead_quality": t["lead_quality"]})
    rows.sort(key=lambda r: -r["lead_score"])
    return TEMPLATES.TemplateResponse("dashboard.html", {
        "request": request,
        "rows": rows,
        "pipeline": case_service.pipeline_overview(data["intakes"]),
        "analytics": analytics_service.firm_analytics(data["intakes"]),
        "stale": case_service.stale_intakes(data["intakes"]),
    })


@app.get("/portal/{intake_id}", response_class=HTMLResponse)
def portal(request: Request, intake_id: int):
    profile = case_service.client_profile(intake_id, _data())
    if not profile:
        raise HTTPException(status_code=404, detail="Client not found")
    return TEMPLATES.TemplateResponse("portal.html", {
        "request": request,
        "profile": profile,
        "pipeline_stages": case_service.PIPELINE,
    })
