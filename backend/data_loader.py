"""
Data loader — the single boundary to the data sources (client intakes,
lawyers, appointments, documents). In production these come from a CRM /
database; here they are JSON scenario datasets.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DATASETS = ("lawyers", "intakes", "appointments", "documents")


def _load(name: str) -> list:
    return json.loads((DATA_DIR / f"{name}.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_data() -> dict:
    return {name: _load(name) for name in DATASETS}


@lru_cache(maxsize=1)
def load_knowledge_base() -> list:
    return _load("legal_faq")
