from fastapi.testclient import TestClient
from src.aims.api import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_positive_sentiment():
    r = client.post("/analyze", json={"text": "I love this"})
    data = r.json()
    assert data["sentiment"] == "positive"
    assert "love" in data["matched_positive"]


def test_negative_sentiment_escalates():
    r = client.post("/analyze", json={"text": "this is terrible"})
    data = r.json()
    assert data["sentiment"] == "negative"
    assert data["escalate"] is True
    assert data["issue"] == "negative_sentiment"


def test_mixed_sentiment_neutral():
    r = client.post("/analyze", json={"text": "I love it but it is awful"})
    data = r.json()
    assert data["sentiment"] == "neutral"
    assert data["escalate"] is False
