def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_seed_counts(client):
    s = client.get("/api/v1/stats").json()
    assert s["total_drives"] == 100
    assert s["telemetry_records"] == 3000
    assert s["low"] + s["medium"] + s["high"] == 100
    assert s["high"] > 0


def test_list_and_filter(client):
    r = client.get("/api/v1/drives?risk_level=HIGH").json()
    assert r["total"] > 0 and all(d["risk_level"] == "HIGH" for d in r["items"])
    assert r["items"][0]["latest"] is not None


def test_pagination(client):
    r = client.get("/api/v1/drives?limit=10&offset=0").json()
    assert len(r["items"]) == 10 and r["total"] == 100


def test_get_drive_and_404(client):
    assert client.get("/api/v1/drives/1").json()["name"] == "drive-001"
    assert client.get("/api/v1/drives/9999").status_code == 404


def test_at_risk_route_not_shadowed(client):
    r = client.get("/api/v1/drives/at-risk?min_level=HIGH")
    assert r.status_code == 200 and all(d["risk_level"] == "HIGH" for d in r.json())


def test_history(client):
    h = client.get("/api/v1/drives/1/history").json()
    assert len(h) == 30
    assert h[0]["timestamp"] < h[-1]["timestamp"]
    assert client.get("/api/v1/drives/9999/history").status_code == 404


def test_incident_lifecycle(client):
    r = client.post("/api/v1/incidents", json={"drive_id": 1, "description": "test"})
    assert r.status_code == 201
    inc = r.json()
    assert inc["status"] == "OPEN" and inc["severity"] in ("LOW", "MEDIUM", "HIGH")
    p = client.patch(f"/api/v1/incidents/{inc['id']}", json={"status": "RESOLVED"}).json()
    assert p["status"] == "RESOLVED" and p["resolved_at"] is not None
    assert client.patch("/api/v1/incidents/999", json={"status": "OPEN"}).status_code == 404
    assert client.patch(f"/api/v1/incidents/{inc['id']}", json={"status": "BOGUS"}).status_code == 422


def test_incident_unknown_drive(client):
    assert client.post("/api/v1/incidents", json={"drive_id": 9999}).status_code == 404
