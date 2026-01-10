from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}

class MessageIn(BaseModel):
    message: str


def handle_message(message: str) -> dict:
    """
    Default handler - tests monkeypatch this.
    """
    return {
        "route": "default"
        "issue": None
        "reply": "ok"
    }

@app.post("/handle")
def handle(msg: MessageIn):
    return handle_message(msg.message)


@app.get("/health")
def health():
    return {"status": "ok"}
