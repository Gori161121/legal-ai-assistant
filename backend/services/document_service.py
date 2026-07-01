"""
Document Service

Generates the required-document checklist for a matter and reports which
documents have been received for a given intake.
"""
from __future__ import annotations

CHECKLISTS = {
    "Family": ["ID copy", "Marriage certificate", "Financial statement"],
    "Employment": ["ID copy", "Employment contract", "Termination letter"],
    "Corporate": ["Founders' IDs", "Draft charter", "Shareholder details"],
    "Contract": ["ID copy", "Signed contract", "Correspondence"],
    "Immigration": ["Passport copy", "Application form", "Supporting letters"],
    "Real Estate": ["ID copy", "Property documents", "Draft contract"],
    "IP": ["ID copy", "Brand/logo files", "Prior use evidence"],
    "Criminal": ["ID copy", "Case summons", "Any evidence"],
    "General": ["ID copy"],
}


def checklist_for(practice_area: str) -> list:
    return CHECKLISTS.get(practice_area, CHECKLISTS["General"])


def document_status(intake_id: int, documents: list) -> dict:
    items = [d for d in documents if d.get("intake_id") == intake_id]
    received = [d["name"] for d in items if d.get("received")]
    missing = [d["name"] for d in items if not d.get("received")]
    total = len(items)
    return {
        "intake_id": intake_id,
        "total_required": total,
        "received": received,
        "missing": missing,
        "completion_pct": round(len(received) / total * 100, 1) if total else 0.0,
    }
