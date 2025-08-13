from fastapi import FastAPI

app = FastAPI(title="Profile Service")


@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "profile"}
