from fastapi import FastAPI

app = FastAPI()

def log_event(payload):
    # placeholder for telemetry (tests monkeypatch this)
    pass

def handle_message(message: str):
    return {
        "route": "human_billing",
        "issue": "billing",
        "reply": "Test reply",
    }

@app.get("/health")
def health():
    return {"status": "ok"}
