"""
Firm Analytics

Intake funnel, acquisition channel mix, practice-area demand and lead quality —
the numbers a firm's partners use to run the practice.
"""
from __future__ import annotations

from collections import Counter

from . import triage_service


def firm_analytics(intakes: list) -> dict:
    total = len(intakes)
    channels = Counter(i.get("channel", "unknown") for i in intakes)

    area_demand: Counter = Counter()
    scores = []
    for i in intakes:
        area = triage_service.classify_practice_area(i.get("description", ""))
        area_demand[area] += 1
        scores.append(triage_service.lead_score(i, area))

    converted = sum(1 for i in intakes if i.get("status") == "converted")
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0.0

    return {
        "total_intakes": total,
        "conversion_rate_pct": round(converted / total * 100, 1) if total else 0.0,
        "avg_lead_score": avg_score,
        "channel_mix": dict(channels.most_common()),
        "practice_area_demand": dict(area_demand.most_common()),
    }
