from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
import time
import uuid

app = FastAPI()
STARTED_AT = datetime.now(timezone.utc).isoformat()


class MessageIn(BaseModel):
    message: str


def log_event(payload):
    # stub - tests monkeypatch this
    return None


@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1",
        "started_at": STARTED_AT,
    }


@app.post("/analyze")
def analyze(payload: dict):
    text = (payload.get("text") or "").lower()

    matched_positive = []
    matched_negative = []

    issue = None
    escalate = False
    score = 0.5 # default

    if "love" in text:
        matched_positive.append("love")

    if "terrible" in text or "awful" in text:
        matched_negative.append("terrible" if "terrible" in text else "awful")
        issue = "negative_sentiment"
        escalate = True

    # Determine sentiment
    if matched_negative and matched_positive:
        sentiment = "neutral"
        escalate = False
        issue = None
    elif matched_negative:
        sentiment = "negative"
        score = 0.2
    elif matched_positive:
        sentiment = "positive"
        score = 0.8
    else:
        sentiment = "neutral"

    return {
        "request_id": str(uuid.uuid4()),
        "version": "1.0.0",
        "sentiment": sentiment,  
        "score": score,
        "escalate": escalate,
        "issue": issue,
        "matched_positive": matched_positive,
        "matched_negative": matched_negative,
        "explanation": (
            "No sentiment keywords matched."
            if not (matched_positive or matched_negative)
            else "Keywords matched."
        ),
        "route": "sentiment_v1",
}


@app.post("/v1/handle")
def handle(msg: MessageIn):
    start = time.perf_counter()

    analysis = analyze({"text": msg.message})

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Telemetry
    log_event(
        {
            "type": "handle_message",
            "route": analysis.get("route"),
            "issue": analysis.get("issue"),
        }
    )

    return {
        "version": "1.0.0",
        "started_at": STARTED_AT,
        "route": "sentiment_v1",
        "issue": analysis.get("issue"),
        "reply": f"Sentiment detected: {analysis.get('sentiment')}",
        "confidence": analysis.get("score", 0.5),
        "escalate": analysis.get("escalate", False),
        "meta": {
            "ts": STARTED_AT,
            "elapsed_ms": elapsed_ms,
            **analysis,
        },
    }
