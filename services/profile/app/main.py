from fastapi import FastAPI

from .metrics import MetricsMiddleware, metrics

app = FastAPI(title="Profile Service")
app.add_middleware(MetricsMiddleware)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "profile"}


@app.get("/readyz")
def readyz():
    return {"status": "ok"}


@app.get("/metrics")
def metrics_endpoint():
    return metrics()
