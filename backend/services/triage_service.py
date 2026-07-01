"""
Triage Engine

Classifies a client's matter into a practice area, estimates urgency and
complexity, and produces a lead-quality score so the firm can prioritise.

IMPORTANT: this is triage/routing only — it is NOT legal advice.
"""
from __future__ import annotations

PRACTICE_KEYWORDS = {
    "Family": ["divorce", "custody", "marriage", "child", "alimony"],
    "Employment": ["employer", "wages", "termination", "fired", "salary", "workplace"],
    "Corporate": ["company", "shareholder", "register", "incorporat", "charter"],
    "Contract": ["contract", "breach", "invoice", "agreement", "supplier", "lawsuit"],
    "Immigration": ["visa", "residence permit", "immigration", "passport", "citizenship"],
    "Real Estate": ["apartment", "landlord", "deposit", "property", "rental", "purchase"],
    "IP": ["trademark", "brand", "copyright", "patent"],
    "Criminal": ["criminal", "charged", "offence", "offense", "arrest", "police"],
}

COMPLEXITY = {
    "Criminal": "high", "Corporate": "high", "Immigration": "medium",
    "Employment": "medium", "Contract": "medium", "Family": "medium",
    "Real Estate": "low", "IP": "medium", "General": "low",
}

URGENCY_POINTS = {"high": 40, "medium": 25, "low": 10}


def classify_practice_area(description: str) -> str:
    text = (description or "").lower()
    best, best_hits = "General", 0
    for area, keywords in PRACTICE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in text)
        if hits > best_hits:
            best, best_hits = area, hits
    return best


def lead_score(intake: dict, practice_area: str) -> int:
    score = URGENCY_POINTS.get(intake.get("urgency", "low"), 10)
    if intake.get("contact_email"):
        score += 20
    if intake.get("contact_phone"):
        score += 20
    if practice_area != "General":
        score += 20
    return min(100, score)


def triage_intake(intake: dict) -> dict:
    area = classify_practice_area(intake.get("description", ""))
    score = lead_score(intake, area)
    quality = "hot" if score >= 80 else "warm" if score >= 55 else "cold"

    return {
        "intake_id": intake.get("id"),
        "practice_area": area,
        "urgency": intake.get("urgency", "low"),
        "complexity": COMPLEXITY.get(area, "low"),
        "lead_score": score,
        "lead_quality": quality,
        "conflict_check": "no_conflict_detected",
        "recommended_next_step": "Schedule a consultation with a matching lawyer.",
    }
