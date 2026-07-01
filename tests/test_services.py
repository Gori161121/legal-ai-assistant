from backend.services import (
    analytics_service,
    case_service,
    conflict_service,
    conversation_service,
    document_service,
    intake_service,
    rag_service,
    routing_service,
    scheduling_service,
    triage_service,
)


def test_classify_practice_area():
    assert triage_service.classify_practice_area("I need a divorce and child custody") == "Family"
    assert triage_service.classify_practice_area("trademark for my brand") == "IP"
    assert triage_service.classify_practice_area("hello there") == "General"


def test_triage_lead_score(data):
    intake = data["intakes"][0]
    result = triage_service.triage_intake(intake)
    assert 0 <= result["lead_score"] <= 100
    assert result["lead_quality"] in {"hot", "warm", "cold"}


def test_intake_validation():
    ok = intake_service.build_intake({"client_name": "A", "description": "x", "contact_email": "a@b.c"})
    assert ok["is_valid"]
    bad = intake_service.build_intake({"client_name": "", "description": ""})
    assert not bad["is_valid"]
    assert "contact_email_or_phone" in bad["missing_fields"]


def test_routing_matches_area(data):
    workload = routing_service.current_workload(data["intakes"])
    result = routing_service.suggest_lawyer("Family", data["lawyers"], workload)
    assert result is not None
    assert result["matched_on_area"]


def test_scheduling_slots_weekdays(data):
    slots = scheduling_service.propose_slots(1, data["appointments"], count=3)
    assert len(slots) == 3


def test_rag_retrieves_relevant(kb):
    result = rag_service.retrieve("my employer did not pay my wages", kb, k=2)
    assert result["results"]
    assert result["results"][0]["topic"] == "Employment"
    assert "not legal advice" in result["disclaimer"].lower()


def test_conflict_detects_existing_client(data):
    existing_name = data["intakes"][0]["client_name"]
    result = conflict_service.check_conflict(existing_name, "some matter", data["intakes"])
    assert result["conflict_detected"]
    assert result["status"] == "needs_manual_review"


def test_conflict_clear_for_new_person(data):
    result = conflict_service.check_conflict("Zzz Nonexistent Person", "a contract issue", data["intakes"])
    assert not result["conflict_detected"]


def test_document_status(data):
    intake_id = data["documents"][0]["intake_id"]
    status = document_service.document_status(intake_id, data["documents"])
    assert 0 <= status["completion_pct"] <= 100


def test_conversation_flow(kb):
    convo = conversation_service.start()
    state = convo["state"]
    for msg in ["Jane Doe", "jane@example.com", "I need help with a divorce", "high", "yes"]:
        result = conversation_service.advance(state, msg, kb)
        state = result["state"]
    assert result["complete"]
    assert state["data"]["client_name"] == "Jane Doe"
    assert state["data"]["practice_area"] == "Family"
    assert state["data"]["wants_appointment"] is True


def test_pipeline_and_analytics(data):
    pipe = case_service.pipeline_overview(data["intakes"])
    assert pipe["total_intakes"] == len(data["intakes"])
    ana = analytics_service.firm_analytics(data["intakes"])
    assert ana["total_intakes"] == len(data["intakes"])
    assert ana["practice_area_demand"]
