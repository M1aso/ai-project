from fastapi import FastAPI
app = FastAPI(title="Notifications Service")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "notifications" }
