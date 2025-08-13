from fastapi import FastAPI

from .metrics import MetricsMiddleware, metrics
from .routers import email

app = FastAPI(title="Auth Service")
app.add_middleware(MetricsMiddleware)
app.include_router(email.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    return metrics()
