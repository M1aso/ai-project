from fastapi import FastAPI

from .routers import notify

app = FastAPI(title="Notifications Service")
app.include_router(notify.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "notifications"}


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "notifications"}

@app.get("/api/healthz")
def api_healthz():
    return {"status": "ok", "service": "notifications"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


@app.get("/metrics")
def metrics():  # pragma: no cover - placeholder
    return ""
