from fastapi import FastAPI
app = FastAPI(title="Content Service")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "service": "content" }
