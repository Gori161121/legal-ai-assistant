"""
Routing Service

Assigns an intake to the best-matching lawyer by practice area, balancing by
current workload (fewest open intakes wins ties).
"""
from __future__ import annotations


def suggest_lawyer(practice_area: str, lawyers: list, workload: dict | None = None) -> dict | None:
    workload = workload or {}
    matching = [law for law in lawyers if practice_area in law.get("practice_areas", [])]
    pool = matching or lawyers
    if not pool:
        return None
    # Pick the matching lawyer with the lightest current workload.
    best = min(pool, key=lambda law: workload.get(law["id"], 0))
    return {
        "lawyer_id": best["id"],
        "lawyer_name": best["name"],
        "practice_area": practice_area,
        "matched_on_area": bool(matching),
    }


def current_workload(intakes: list) -> dict:
    """Open intakes per assigned lawyer."""
    load: dict[int, int] = {}
    for i in intakes:
        lid = i.get("assigned_lawyer_id")
        if lid and i.get("status") == "open":
            load[lid] = load.get(lid, 0) + 1
    return load
