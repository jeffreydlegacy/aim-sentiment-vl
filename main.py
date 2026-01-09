from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal, Optional, List
import uuid
from collections import Counter
from threading import Lock
from time import time
from datetime import datetime, timezone
import json
from pathlib import Path

AIM_VERSION = "1.0.0"

app = FastAPI(
    title="AIM Sentiment v1",
    version=AIM_VERSION,
)

METER_LOG = Path("meter.jsonl")
ESCALATE_LOG = Path("escalations.jsonl")

START_TS = time()
COUNTS_LOCK = Lock()
TOTAL_REQUESTS = 0
BY_ENDPOINT = Counter ()
LAST_TS = None
ESCALATE_COUNT = 0


# ---------- Models ----------
class SentimentRequest(BaseModel):
    text: str


class SentimentResponse(BaseModel):
    request_id: str
    version: str
    sentiment: Literal["positive", "neutral", "negative"]
    score: float
    escalate: bool = False
    
    matched_positive: list[str] = Field(default_factory=list)
    matched_negative: list[str] = Field(default_factory=list)
    explanation: str = ""

    # optional fields (future-proof)
    route: Optional[str] = "sentiment_vl",
    issue: Optional[str] = None



# ---------- Metering ----------
def log_call(request_id: str, endpoint: str) -> None:
    global TOTAL_REQUESTS, LAST_TS

    ts = datetime.now(timezone.utc).isoformat()
    event = {
        "ts": ts,
        "request_id": request_id,
        "endpoint": endpoint,
    }

    # in-memory counters (fast)
    with COUNTS_LOCK:
        TOTAL_REQUESTS += 1
        BY_ENDPOINT[endpoint] += 1
        LAST_TS = ts

    # file log (durable)
    with METER_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok", "version": AIM_VERSION}


@app.get("/metrics")
def metrics():
    with COUNTS_LOCK:
        return {
            "uptime_seconds": round(time() - START_TS, 2),
            "total_requests": TOTAL_REQUESTS,
            "by_endpoint": dict(BY_ENDPOINT),
            "last_request_at": LAST_TS,
            "log_file": str(METER_LOG),
        }

          
@app.post("/analyze", response_model=SentimentResponse)
def analyze(req: SentimentRequest):
    request_id = str(uuid.uuid4())
    log_call(request_id, "/analyze")
 
    text = req.text.lower()



    # VERY simple heuristic (placeholder)
    positive_words = ["good", "great", "love", "excellent", "happy"]
    negative_words = ["bad", "terrible", "hate", "awful", "sad"]

    matched_positive = [w for w in positive_words if w in text]
    matched_negative = [w for w in negative_words if w in text]
   
    sentiment: Literal["positive", "neutral", "negative"] = "neutral"
    score = 0.5
    explanation = "No sentiment keywords matched."
    escalate = False
    issue = None

    if matched_positive and matched_negative:
        sentiment = "neutral"
        score = 0.5
        explanation = (
            f"Matched positive keywords: ({', '.join(matched_positive)}) "
            f"and negative ({', '.join(matched_negative)}); returning neutral."
        )

    elif matched_positive:
        sentiment = "positive"
        score = 0.9
        explanation = f"Matched positive keywords: ({', '.join(matched_positive)}"

    elif matched_negative:
        sentiment = "negative"
        score = 0.1
        explanation = f"Matched negative keywords: ({', '.join(matched_negative)}"   
        escalate = True
        issue = "negative_sentiment"


    # escalation tracking (CORRECT LOCATION)
    global ESCALATE_COUNT
    ESCALATE_COUNT += 1

    log_escalation({
        "ts": datetime.now(timezone.utc).isoformat(),
        "request_id": request_id,
        "endpoint": "/analyze",
        "text": req.text,
        "matched_negative": matched_negative,
    }) 
 

    return SentimentResponse(
        request_id=request_id,
        version=AIM_VERSION,
        sentiment=sentiment,
        score=score,
        matched_positive=matched_positive,
        matched_negative=matched_negative,
        explanation=explanation,
        escalate=escalate,
        route="sentiment_vl",
        issue=issue
    )
