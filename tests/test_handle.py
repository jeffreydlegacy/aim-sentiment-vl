import pytest
from fastapi.testclient import TestClient

@pytest.fixture()
def client():
    from aims.api import app
    return TestClient(app)


def test_health__ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"


def test_handle_positive(client):
    r = client.post("/v1/handle", json={"message": "I love this"})
    assert r.status_code == 200
    data = r.json()
    assert data["confidence"] > 0.5
    assert data["escalate"] is False


def test_handle_negative_escalates(client):
    r = client.post("/v1/handle", json={"message": "this is terrible"})
    assert r.status_code == 200
    data = r.json()
    assert data["escalate"] is True


def test_handle_mixed_sentiment_neutral(client):
    r = client.post(
    "/v1/handle",
    json={"message": "I love it but it is terrible"}
    )
    assert r.status_code == 200
    data = r.json()

    assert data["confidence"] == 0.5
    assert data["escalate"] is False

def test_handle_neutral_low_confidence_escalates(client):
    r = client.post("/v1/handle", json={"message": "Hmm. Not sure."})
    assert r.status_code == 200
    data = r.json()

    # This is the "no keywords" neutral case -> should trigger low_confidence escalation
    assert data["issue"] == "low_confidence"
    assert data["escalate"] is True
    assert data["confidence"] == 0.5
