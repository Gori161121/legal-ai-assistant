"""
Notification Service

Builds the SMS and email messages a client receives as their matter moves
through the pipeline. This module composes the messages (delivery would be
handled by an SMS/email provider in production).
"""
from __future__ import annotations

STAGE_MESSAGES = {
    "new": "We've received your request and will review it shortly.",
    "triaged": "Your matter has been reviewed and assigned to a specialist lawyer.",
    "consultation_scheduled": "Your consultation is scheduled. See the details in your portal.",
    "engaged": "Welcome aboard — we are now handling your case.",
    "in_progress": "There's an update on your case. Check your portal for details.",
    "closed": "Your case has been closed. Thank you for choosing our firm.",
}


def build_notifications(intake: dict) -> list:
    stage = intake.get("stage", "new")
    body = STAGE_MESSAGES.get(stage, "Your case has an update.")
    name = intake.get("client_name", "Client")
    messages = []

    if intake.get("contact_email"):
        messages.append({
            "channel": "email",
            "to": intake["contact_email"],
            "subject": f"Update on your matter ({stage})",
            "body": f"Dear {name}, {body}",
        })
    if intake.get("contact_phone"):
        messages.append({
            "channel": "sms",
            "to": intake["contact_phone"],
            "body": f"{name}: {body}",
        })
    return messages
