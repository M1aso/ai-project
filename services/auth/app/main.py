from fastapi import FastAPI

from .metrics import setup_metrics
from .routers import email

app = FastAPI(title="Auth Service")
app.include_router(email.router)
setup_metrics(app)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth"}


@app.get("/readyz")
def readyz():
    return {"status": "ok", "service": "auth"}
