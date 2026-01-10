from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()
STARTED_AT = datetime.utcnow().isoformat()

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

@app.post("/v1/handle")
def handle(msg: MessageIn):
    result = handle_message(msg.message)

    log_event({
        "type": "handle_message",
        "route": result.get("route"),
        "issue": result.get("issue"),
    })

    return result

