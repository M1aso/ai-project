from fastapi import FastAPI

app = FastAPI(title="Analytics Service")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "analytics"}
