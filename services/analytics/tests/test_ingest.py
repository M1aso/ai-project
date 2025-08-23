from datetime import datetime, timezone
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.analytics.app.db.models import Base, Event, get_db
from services.analytics.app.routers.ingest import (
    router as ingest_router,
    MAX_BATCH_SIZE,
)


def setup_app():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(ingest_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app, TestingSessionLocal


def test_ingest_and_limit():
    app, SessionLocal = setup_app()
    client = TestClient(app)

    events = [
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_id": "u1",
            "type": "click",
            "payload": {"a": 1},
        },
        {
            "ts": datetime.now(timezone.utc).isoformat(),
            "user_id": "u2",
            "type": "view",
            "payload": {"b": 2},
        },
    ]
    resp = client.post("/api/analytics/ingest", json=events)
    assert resp.status_code == 200
    assert resp.json() == {"ingested": 2}

    db = SessionLocal()
    assert db.query(Event).count() == 2
    db.close()

    big_batch = events * (MAX_BATCH_SIZE // len(events) + 1)
    resp = client.post("/api/analytics/ingest", json=big_batch)
    assert resp.status_code == 413
