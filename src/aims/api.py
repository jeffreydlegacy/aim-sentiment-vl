from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import time
import uuid

app = FastAPI()
STARTED_AT = datetime.now(timezone.utc).isoformat()


class MessageIn(BaseModel):
    message: str

class AnalyzeIn(BaseModel):
    text: str

class AnalyzeOut(BaseModel):
    request_id: str
    version: str
    sentiment: str
    score: float
    escalate: bool
    issue: Optional[str]
    matched_positive: List[str]
    matched_negative: List[str]
    explanation: str
    route: str


class HandleOut(BaseModel):
    version: str
    started_at: str
    route: str
    issue: Optional[str] = None
    reply: str
    confidence: float
    escalate: bool
    meta: Dict[str, Any]    


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


@app.post("/analyze", response_model=AnalyzeOut)
def analyze(payload: AnalyzeIn) -> AnalyzeOut:
    text = payload.text.lower()

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

    # Determine sentiment + score
    pos = len(matched_positive)
    neg = len(matched_negative)

    if pos and neg:
        sentiment = "neutral"
        score = 0.5
        escalate = False
        issue = None
    elif neg:
        sentiment = "negative"
        score = 0.3 if neg == 1 else 0.15
    elif pos:
        sentiment = "positive"
        score = 0.7 if pos == 1 else 0.85
    else:
        sentiment = "neutral"
        score = 0.5
        escalate = True
        issue = "low_confidence"

    return AnalyzeOut(
        request_id=str(uuid.uuid4()),
        version="1.0.0",
        sentiment=sentiment,
        score=score,
        escalate=escalate,
        issue=issue,
        matched_positive=matched_positive,
        matched_negative=matched_negative,
        explanation=(
            "No sentiment keywords matched."
            if not (matched_positive or matched_negative)
            else "Keywords matched."
        ),
        route="sentiment_v1",
    )


@app.post(
    "/v1/handle",
    response_model=HandleOut,
    response_model_exclude_none=True
)

def handle(msg: MessageIn):
    start = time.perf_counter()

    analysis = analyze(AnalyzeIn(text=msg.message))

    elapsed_ms = int((time.perf_counter() - start) * 1000)

    # Telemetry
    log_event(
        {
            "type": "handle_message",
            "route": analysis.route,
            "issue": analysis.issue,
            "request_id": analysis.request_id,
        }
    )

    # A11: confidence-based escalation
    if analysis.score < 0.4 or (
        analysis.sentiment == "neutral"
        and not analysis.matched_positive
        and not analysis.matched_negative
    ):
        analysis.escalate = True
        analysis.issue = analysis.issue or "low_confidence"

    return {
        "version": "1.0.0",
        "started_at": STARTED_AT,
        "route": "sentiment_v1",
        "issue": analysis.issue,
        "reply": f"Sentiment detected: {analysis.sentiment}",
        "confidence": analysis.score,
        "escalate": analysis.escalate,
        "meta": {
            "ts": STARTED_AT,
            "elapsed_ms": elapsed_ms,
            "request_id": analysis.request_id,
        },
    }
