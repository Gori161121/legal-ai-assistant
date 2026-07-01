"""
Case Pipeline & Client Profile

Tracks where each matter sits in the pipeline, assembles a full client profile
(intake + lawyer + appointment + documents) and flags stale intakes that need
follow-up.
"""
from __future__ import annotations

from datetime import date, datetime

from . import document_service, notification_service, triage_service

PIPELINE = ["new", "triaged", "consultation_scheduled", "engaged", "in_progress", "closed"]


def _days_since(iso: str, as_of: date) -> int:
    try:
        return (as_of - datetime.strptime(iso, "%Y-%m-%d").date()).days
    except Exception:
        return 0


def pipeline_overview(intakes: list) -> dict:
    counts = {stage: 0 for stage in PIPELINE}
    for i in intakes:
        counts[i.get("stage", "new")] = counts.get(i.get("stage", "new"), 0) + 1
    total = len(intakes)
    converted = sum(1 for i in intakes if i.get("status") == "converted")
    lost = sum(1 for i in intakes if i.get("status") == "lost")
    return {
        "total_intakes": total,
        "by_stage": counts,
        "conversion_rate_pct": round(converted / total * 100, 1) if total else 0.0,
        "lost_rate_pct": round(lost / total * 100, 1) if total else 0.0,
    }


def client_profile(intake_id: int, data: dict) -> dict | None:
    intake = next((i for i in data["intakes"] if i["id"] == intake_id), None)
    if not intake:
        return None

    lawyer = next((law for law in data["lawyers"]
                   if law["id"] == intake.get("assigned_lawyer_id")), None)
    appointment = next((a for a in data["appointments"]
                        if a.get("intake_id") == intake_id), None)
    triage = triage_service.triage_intake(intake)

    return {
        "intake": intake,
        "practice_area": triage["practice_area"],
        "stage": intake.get("stage"),
        "assigned_lawyer": lawyer["name"] if lawyer else "Unassigned",
        "appointment": appointment,
        "documents": document_service.document_status(intake_id, data["documents"]),
        "latest_notification": (notification_service.build_notifications(intake) or [None])[0],
    }


def stale_intakes(intakes: list, days: int = 7, as_of: date | None = None) -> list:
    as_of = as_of or date.today()
    stale = []
    for i in intakes:
        if i.get("stage") in ("new", "triaged") and i.get("status") == "open":
            age = _days_since(i.get("created_at", ""), as_of)
            if age >= days:
                stale.append({
                    "intake_id": i["id"],
                    "client_name": i["client_name"],
                    "stage": i["stage"],
                    "days_waiting": age,
                })
    stale.sort(key=lambda r: -r["days_waiting"])
    return stale
