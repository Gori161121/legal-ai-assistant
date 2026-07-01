from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_intakes_endpoint():
    r = client.get("/intakes")
    assert r.status_code == 200
    assert len(r.json()) == 30


def test_triage_endpoint():
    r = client.get("/intake/1/triage")
    assert r.status_code == 200
    assert "practice_area" in r.json()


def test_triage_404():
    assert client.get("/intake/9999/triage").status_code == 404


def test_knowledge_search():
    r = client.get("/knowledge/search", params={"q": "visa residence permit"})
    assert r.status_code == 200
    assert r.json()["results"][0]["topic"] == "Immigration"


def test_conversation_endpoint():
    start = client.post("/intake/chat", json={}).json()
    sid = start["session_id"]
    assert start["message"]
    for msg in ["Jane Doe", "jane@example.com", "divorce and custody", "high", "yes"]:
        resp = client.post("/intake/chat", json={"session_id": sid, "message": msg}).json()
    assert resp["complete"]
    assert resp["collected"]["practice_area"] == "Family"


def test_pages_render():
    for path in ("/", "/dashboard", "/portal/1"):
        r = client.get(path)
        assert r.status_code == 200
        assert "text/html" in r.headers["content-type"]
