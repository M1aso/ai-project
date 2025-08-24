from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.analytics.app.db.database import get_db
from services.analytics.app.db.models import Base, Event
from services.analytics.app.routers.reports import router as reports_router


def setup_app():
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:5432/test_aiproject",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(reports_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app, TestingSessionLocal


def seed_events(SessionLocal):
    db = SessionLocal()
    now = datetime.now(timezone.utc)
    yesterday = now - timedelta(days=1)
    db.add_all(
        [
            Event(ts=now, user_id="u1", type="click", payload={}),
            Event(ts=now, user_id="u2", type="view", payload={}),
            Event(ts=yesterday, user_id="u3", type="view", payload={}),
        ]
    )
    db.commit()
    db.close()


def test_dau_and_export_csv():
    app, SessionLocal = setup_app()
    seed_events(SessionLocal)
    client = TestClient(app)

    resp = client.get("/api/analytics/reports/dau")
    assert resp.status_code == 200
    assert resp.json()["dau"] == 2

    resp = client.get("/api/analytics/reports/events", params={"format": "csv"})
    assert resp.status_code == 200
    lines = resp.text.strip().splitlines()
    assert lines[0] == "ts,user_id,type,src"
    assert len(lines) == 4
