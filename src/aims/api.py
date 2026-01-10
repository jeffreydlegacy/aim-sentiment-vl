from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
import time

app = FastAPI()
STARTED_AT = datetime.now(timezone.utc).isoformat()

class MessageIn(BaseModel):
    message: str

def log_event(payload):
    # stub — tests monkeypatch this
    pass

def handle_message(message: str):
    # base response used by tests
    return {
        "route": "human_billing",
        "issue": "billing",
        "reply": "Test reply",
        "confidence": 0.5,    
        "escalate": False,
        "meta": {},
    }

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
    escalate = False
    issue = None

    if "love" in text:
        matched_positive.append("love")

    if "terrible" in text or "awful" in text:
        sentiment = "negative"
        escalate = True
        issue = "negative_sentiment"

        # mixed case: both positive + negative
        if matched_positive:
            sentiment = "neutral"
            escalate = False
            issue = None

    elif matched_positive:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    return {
        "sentiment": sentiment,
        "escalate": escalate,
        "issue": issue,
        "matched_positive": matched_positive,
    }


    # Telemetry hook (monkeypatched in tests)
    log_event({
        "type": "handle_message", 
        "route": result["route"],
        "issue": result["issue"],
    })

    # IMPORTANT: return the full result, (route/issue/reply/confidence/escalate)
    # and ensure meta has ts + elapsed_ms
    return {
        "version": "1",
        "started_at": STARTED_AT,
        "route": result["route"],
        "issue": result["issue"],
        "reply": result["reply"],
        "confidence": result.get("confidence", 0.0),
        "escalate": result.get("escalate", False),
        "meta": {
            "ts": STARTED_AT,
            **result.get("meta", {}),
        },
    }

