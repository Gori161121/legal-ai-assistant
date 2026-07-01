"""
Conflict-of-Interest Check

Before the firm engages, it must ensure it isn't already acting for the
opposing party. This does a first-pass check of a new client against existing
intakes (by name and by opposing party mentioned in the description).

A real firm confirms manually — this flags matters that need review.
"""
from __future__ import annotations


def check_conflict(new_client_name: str, description: str, existing_intakes: list) -> dict:
    name = (new_client_name or "").strip().lower()
    text = (description or "").lower()

    flags = []
    for intake in existing_intakes:
        existing = (intake.get("client_name") or "").strip().lower()
        if not existing:
            continue
        # Same person already a client.
        if existing == name:
            flags.append({"type": "existing_client", "matched": intake.get("client_name"),
                          "intake_id": intake.get("id")})
        # Existing client named as the opposing party in the new matter.
        elif existing and existing in text:
            flags.append({"type": "possible_opposing_party", "matched": intake.get("client_name"),
                          "intake_id": intake.get("id")})

    return {
        "conflict_detected": bool(flags),
        "status": "needs_manual_review" if flags else "clear",
        "flags": flags,
    }
