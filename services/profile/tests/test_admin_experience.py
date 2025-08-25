import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.append(str(Path(__file__).resolve().parents[3]))

from services.profile.app.auth import get_current_user
from services.profile.app.db.database import get_db
from services.profile.app.db.models import Base
from services.profile.app.routers.admin_experience import router as admin_router


def setup_app():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(admin_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def mock_get_current_user(request: Request):
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            # Parse the test token format: "user_id" or "user_id:role1,role2"
            if ":" in token:
                user_id, roles_part = token.split(":", 1)
                roles = roles_part.split(",")
            else:
                user_id = token
                roles = []
            return {"user_id": user_id, "roles": roles}
        return {"user_id": "test-user", "roles": []}

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    return app, TestingSessionLocal


def auth_header(user_id: str, roles=None):
    token = user_id
    if roles:
        token += ":" + ",".join(roles)
    return {"Authorization": f"Bearer {token}"}


def test_non_admin_forbidden():
    app, _ = setup_app()
    client = TestClient(app)
    resp = client.get(
        "/api/admin/experience-levels",
        headers=auth_header("u1"),
    )
    assert resp.status_code == 403


def test_crud_experience_levels():
    app, _ = setup_app()
    client = TestClient(app)
    headers = auth_header("admin", ["admin"])

    resp = client.post(
        "/api/admin/experience-levels",
        json={"label": "Junior", "sequence": 1},
        headers=headers,
    )
    assert resp.status_code == 200
    level_id = resp.json()["id"]

    resp = client.get(
        "/api/admin/experience-levels",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()[0]["label"] == "Junior"

    resp = client.put(
        f"/api/admin/experience-levels/{level_id}",
        json={"label": "Junior+", "sequence": 2},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["label"] == "Junior+"

    resp = client.delete(
        f"/api/admin/experience-levels/{level_id}",
        headers=headers,
    )
    assert resp.status_code == 204

    resp = client.get(
        "/api/admin/experience-levels",
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []
