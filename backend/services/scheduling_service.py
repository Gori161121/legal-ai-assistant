"""
Scheduling Service

Proposes consultation slots (next business days, fixed working hours) that
don't clash with a lawyer's existing appointments, and confirms a booking.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta

WORKING_HOURS = [10, 11, 14, 15, 16]


def _booked_slots(lawyer_id: int, appointments: list) -> set:
    return {
        a["scheduled_at"]
        for a in appointments
        if a.get("lawyer_id") == lawyer_id and a.get("status") == "scheduled"
    }


def propose_slots(lawyer_id: int, appointments: list,
                  from_date: date | None = None, count: int = 5) -> list:
    from_date = from_date or date.today()
    booked = _booked_slots(lawyer_id, appointments)
    slots = []
    day_offset = 1
    while len(slots) < count and day_offset <= 14:
        d = from_date + timedelta(days=day_offset)
        if d.weekday() < 5:  # weekdays only
            for hour in WORKING_HOURS:
                iso = datetime(d.year, d.month, d.day, hour, 0).isoformat()
                if iso not in booked:
                    slots.append(iso)
                    if len(slots) >= count:
                        break
        day_offset += 1
    return slots


def confirm_appointment(intake_id: int, lawyer_id: int, slot_iso: str) -> dict:
    return {
        "intake_id": intake_id,
        "lawyer_id": lawyer_id,
        "scheduled_at": slot_iso,
        "status": "scheduled",
        "message": "Consultation confirmed.",
    }
