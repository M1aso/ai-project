from fastapi import FastAPI

app = FastAPI(title="Chat Service")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "chat"}
