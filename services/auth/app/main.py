from fastapi import FastAPI
app = FastAPI(title="Auth Service")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "auth" }
