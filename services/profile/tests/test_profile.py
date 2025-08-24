import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.profile.app.db.database import get_db
from services.profile.app.db.models import (
    Base,
    Profile,
    ProfileHistory,
)
from services.profile.app.routers.profile import router as profile_router


def setup_app():
    engine = create_engine(
        "postgresql://postgres:postgres@localhost:5432/test_aiproject",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(profile_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    return app, TestingSessionLocal


def auth_header(user_id: str):
    return {"Authorization": f"Bearer {user_id}"}


def test_profile_get_put_and_history():
    app, SessionLocal = setup_app()
    client = TestClient(app)

    uid = "11111111-1111-1111-1111-111111111111"
    db = SessionLocal()
    db.add(Profile(user_id=uid, first_name="John"))
    db.commit()
    db.close()

    resp = client.get("/api/profile", headers=auth_header(uid))
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "John"

    resp = client.put(
        "/api/profile",
        json={"first_name": "Johnny", "country": "USA"},
        headers=auth_header(uid),
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["first_name"] == "Johnny"
    assert data["country"] == "USA"

    db = SessionLocal()
    history = db.query(ProfileHistory).filter_by(user_id=uid).all()
    fields = {(h.field, h.old_value, h.new_value) for h in history}
    assert ("first_name", "John", "Johnny") in fields
    assert ("country", None, "USA") in fields
    db.close()


def test_profile_validations():
    app, _ = setup_app()
    client = TestClient(app)
    resp = client.put(
        "/api/profile",
        json={"nickname": "x" * 60},
        headers=auth_header("u2"),
    )
    assert resp.status_code == 422

    resp = client.put(
        "/api/profile",
        json={"gender": "invalid", "first_name": "A"},
        headers=auth_header("u2"),
    )
    assert resp.status_code == 422
