"""
Deterministic sample-data generator for the Legal Intake Platform.

Produces lawyers, client intakes, appointments and document checklists as JSON
scenario datasets under backend/data/. Fixed seed = reproducible output.

Run:  python backend/data_generator.py
"""
from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"

LAWYERS = [
    {"id": 1, "name": "Ayşe Rəhimova", "practice_areas": ["Family", "Immigration"]},
    {"id": 2, "name": "Rauf Məmmədov", "practice_areas": ["Corporate", "Contract"]},
    {"id": 3, "name": "Elena Petrova", "practice_areas": ["Employment", "Contract"]},
    {"id": 4, "name": "John Carter", "practice_areas": ["Criminal", "Family"]},
    {"id": 5, "name": "Nigar Alıyeva", "practice_areas": ["Real Estate", "Corporate", "IP"]},
]

# Matter templates: (practice-area signal words live in the text so the triage
# engine has something real to classify).
MATTER_TEMPLATES = [
    ("I am going through a divorce and need help with child custody.", "Family", "high"),
    ("My employer terminated me and has not paid my final wages.", "Employment", "high"),
    ("We want to register a new company and draft a shareholder agreement.", "Corporate", "medium"),
    ("The other party breached our service contract and won't pay.", "Contract", "medium"),
    ("I need help with a residence permit and visa application.", "Immigration", "medium"),
    ("I'm buying an apartment and want the purchase contract reviewed.", "Real Estate", "low"),
    ("Someone is using my brand name; I need trademark protection.", "IP", "medium"),
    ("I have been charged with a criminal offence and need defence.", "Criminal", "high"),
    ("My landlord is refusing to return my deposit after I moved out.", "Real Estate", "low"),
    ("We received a lawsuit over an unpaid invoice from a supplier.", "Contract", "high"),
]

CHANNELS = ["phone", "web", "whatsapp"]
FIRST = ["Murad", "Leyla", "Tom", "Sara", "Kamran", "Emma", "Nina", "Orkhan",
         "Alex", "Farid", "Maria", "Zaur"]
LAST = ["Aliyev", "Smith", "Hasanova", "Brown", "Guliyev", "Johnson", "Ivanova",
        "Mammadli", "Taylor", "Huseynova"]

STAGES = ["new", "triaged", "consultation_scheduled", "engaged", "in_progress", "closed"]

DOC_CHECKLIST = {
    "Family": ["ID copy", "Marriage certificate", "Financial statement"],
    "Employment": ["ID copy", "Employment contract", "Termination letter"],
    "Corporate": ["Founders' IDs", "Draft charter", "Shareholder details"],
    "Contract": ["ID copy", "Signed contract", "Correspondence"],
    "Immigration": ["Passport copy", "Application form", "Supporting letters"],
    "Real Estate": ["ID copy", "Property documents", "Draft contract"],
    "IP": ["ID copy", "Brand/logo files", "Prior use evidence"],
    "Criminal": ["ID copy", "Case summons", "Any evidence"],
}


def generate(seed: int = 11) -> dict:
    rng = random.Random(seed)
    today = date.today()

    intakes, appointments, documents = [], [], []
    appt_id = doc_id = 1

    for i in range(1, 31):
        text, area, urgency = rng.choice(MATTER_TEMPLATES)
        created = today - timedelta(days=rng.randint(0, 29))
        client = f"{rng.choice(FIRST)} {rng.choice(LAST)}"

        # Funnel: not everyone converts.
        roll = rng.random()
        if roll < 0.25:
            stage, status, lawyer_id = "new", "open", None
        elif roll < 0.45:
            stage, status, lawyer_id = "triaged", "open", None
        elif roll < 0.7:
            stage, status, lawyer_id = "consultation_scheduled", "open", None
        elif roll < 0.9:
            stage, status, lawyer_id = rng.choice(["engaged", "in_progress"]), "converted", None
        else:
            stage, status, lawyer_id = "closed", "lost", None

        # Assign a lawyer whose practice area matches (if past triage).
        if stage != "new":
            matching = [law for law in LAWYERS if area in law["practice_areas"]]
            lawyer_id = rng.choice(matching)["id"] if matching else rng.choice(LAWYERS)["id"]

        intake = {
            "id": i,
            "client_name": client,
            "contact_email": f"{client.split()[0].lower()}{i}@example.com",
            "contact_phone": f"+99450{rng.randint(1000000, 9999999)}",
            "channel": rng.choice(CHANNELS),
            "description": text,
            "requested_help": "Consultation and next steps",
            "urgency": urgency,
            "assigned_lawyer_id": lawyer_id,
            "stage": stage,
            "status": status,
            "created_at": created.isoformat(),
        }
        intakes.append(intake)

        # Appointment if scheduled or beyond.
        if stage in ("consultation_scheduled", "engaged", "in_progress", "closed"):
            appt_day = created + timedelta(days=rng.randint(1, 7))
            hour = rng.choice([10, 11, 14, 15, 16])
            appointments.append({
                "id": appt_id,
                "intake_id": i,
                "lawyer_id": lawyer_id,
                "scheduled_at": datetime(appt_day.year, appt_day.month, appt_day.day,
                                         hour, 0).isoformat(),
                "status": "completed" if stage in ("engaged", "in_progress", "closed") else "scheduled",
            })
            appt_id += 1

            for doc_name in DOC_CHECKLIST.get(area, ["ID copy"]):
                documents.append({
                    "id": doc_id,
                    "intake_id": i,
                    "name": doc_name,
                    "required": True,
                    "received": rng.random() > 0.4,
                })
                doc_id += 1

    return {
        "lawyers": LAWYERS,
        "intakes": intakes,
        "appointments": appointments,
        "documents": documents,
    }


def write_datasets() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data = generate()
    for name, rows in data.items():
        (DATA_DIR / f"{name}.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
    print(f"Wrote {sum(len(v) for v in data.values())} records to {DATA_DIR}")


if __name__ == "__main__":
    write_datasets()
