from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MessageIn(BaseModel):
    message: str

def log_event(payload):
    # placeholder for telemetry; tests monkeypatch this
    pass

def handle_message(message: str):
    # default behavior; tests monkeypatch this
    return {
        "route": "human_billing",
        "issue": "billing",
        "reply": "Test reply",
    }

@app.get("/health")
def health():
    return {"status": "ok", "version": "1"}

@app.post("/v1/handle")
def handle(msg: MessageIn):
    result = handle_message(msg.message)

    # IMPORTANT: use the module-level function so monkeypatch works
    log_event({
        "type": "handle_message",
        "route": result.get("route"),
        "issue": result.get("issue"),
    })

    return result
