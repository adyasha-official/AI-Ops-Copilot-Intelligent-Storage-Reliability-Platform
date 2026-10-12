from app.services.rag import search_knowledge


def test_rag_finds_temperature_guidance():
    hits = search_knowledge("what does high temperature indicate")
    assert hits and hits[0]["source"] == "drive_temperature_guidelines.md"


def test_chat_drive_question(client):
    high = client.get("/api/v1/drives?risk_level=HIGH").json()["items"][0]
    r = client.post("/api/v1/chat", json={"message": f"Why is drive {high['id']} at high risk?"}).json()
    assert high["name"] in r["answer"]
    assert "get_drive_status" in r["tools_used"] and r["llm_used"] is False


def test_chat_unknown_drive(client):
    r = client.post("/api/v1/chat", json={"message": "status of drive 9999"}).json()
    assert "couldn't find" in r["answer"]


def test_chat_creates_incident_only_when_asked(client):
    client.post("/api/v1/chat", json={"message": "why is drive 1 risky"})
    assert client.get("/api/v1/incidents").json() == []
    r = client.post("/api/v1/chat", json={"message": "create an incident for drive 1"}).json()
    assert "create_incident" in r["tools_used"]
    assert len(client.get("/api/v1/incidents").json()) == 1


def test_chat_validation(client):
    assert client.post("/api/v1/chat", json={"message": ""}).status_code == 422
