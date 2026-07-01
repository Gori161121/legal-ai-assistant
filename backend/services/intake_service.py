"""
Intake Service

Normalises and validates a raw client contact (from phone, web or WhatsApp)
into a structured intake record, and flags anything missing.
"""
from __future__ import annotations

REQUIRED_FIELDS = ("client_name", "description")
CONTACT_FIELDS = ("contact_email", "contact_phone")
VALID_URGENCY = {"low", "medium", "high"}


def build_intake(raw: dict) -> dict:
    missing = [f for f in REQUIRED_FIELDS if not raw.get(f)]
    if not any(raw.get(f) for f in CONTACT_FIELDS):
        missing.append("contact_email_or_phone")

    urgency = raw.get("urgency", "medium")
    if urgency not in VALID_URGENCY:
        urgency = "medium"

    record = {
        "client_name": raw.get("client_name", "").strip(),
        "contact_email": raw.get("contact_email"),
        "contact_phone": raw.get("contact_phone"),
        "channel": raw.get("channel", "web"),
        "description": (raw.get("description") or "").strip(),
        "requested_help": raw.get("requested_help", "Consultation and next steps"),
        "urgency": urgency,
        "stage": "new",
        "status": "open",
    }

    return {
        "intake": record,
        "is_valid": not missing,
        "missing_fields": missing,
    }
