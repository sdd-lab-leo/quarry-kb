"""API tests for auth and admin user routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.adapters.password_adapter import PasswordAdapter
from app.core.config import Settings, reset_settings_cache
from app.domain.identity import UserRole
from app.main import create_app
from app.models import Base
from app.repositories.database import configure_engine, get_engine, get_session_factory, reset_engine
from app.repositories.user_repository import UserRepository


@pytest.fixture()
def api_client(monkeypatch: pytest.MonkeyPatch, tmp_path):
    db_url = f"sqlite+pysqlite:///{tmp_path / 'auth.db'}"
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("JWT_SIGNING_KEY", "api-test-signing-key-32-bytes-min!!")
    monkeypatch.setenv("AUTH_BOOTSTRAP_ON_STARTUP", "false")
    monkeypatch.setenv("DATABASE_URL", db_url)
    reset_settings_cache()
    reset_engine()

    settings = Settings(
        app_env="local",
        jwt_signing_key="api-test-signing-key-32-bytes-min!!",
        auth_bootstrap_on_startup=False,
        database_url=db_url,
        upload_root="/tmp/quarry-uploads",
        gateway_host_allowlist="gateway.internal",
        embedding_base_url="http://gateway.internal/v1",
        ocr_base_url="http://gateway.internal/v1",
        chat_base_url="http://gateway.internal/v1",
    )
    configure_engine(db_url)
    Base.metadata.create_all(get_engine())
    factory = get_session_factory()
    with factory() as session:
        UserRepository(session).create(
            identifier="admin",
            display_name="Admin",
            role=UserRole.ADMIN,
            password_hash=PasswordAdapter().hash("abcdefghijkl"),
        )
        UserRepository(session).create(
            identifier="viewer",
            display_name="Viewer",
            role=UserRole.VIEWER,
            password_hash=PasswordAdapter().hash("abcdefghijkl"),
        )
        session.commit()

    app = create_app(settings=settings)
    client = TestClient(app)
    yield client
    reset_settings_cache()
    reset_engine()


def _login(client: TestClient, identifier: str, password: str = "abcdefghijkl") -> str:
    response = client.post("/api/v1/auth/login", json={"identifier": identifier, "password": password})
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["token_type"] == "bearer"
    return body["data"]["access_token"]


def test_health_remains_anonymous(api_client: TestClient) -> None:
    response = api_client.get("/api/v1/health/live")
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "alive"


def test_login_validation_envelope(api_client: TestClient) -> None:
    response = api_client.post("/api/v1/auth/login", json={"identifier": "", "password": ""})
    assert response.status_code == 422
    body = response.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION_ERROR"


def test_login_me_and_admin_matrix(api_client: TestClient) -> None:
    token = _login(api_client, "admin")
    me = api_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["data"]["role"] == "Admin"

    listed = api_client.get("/api/v1/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert listed.status_code == 200
    assert len(listed.json()["data"]["items"]) == 2

    created = api_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "identifier": "Editor.One",
            "display_name": "Editor One",
            "password": "abcdefghijkl",
            "role": "Editor",
        },
    )
    assert created.status_code == 201
    assert created.json()["data"]["identifier"] == "editor.one"
    user_id = created.json()["data"]["user_id"]

    viewer_token = _login(api_client, "viewer")
    forbidden = api_client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["error"]["code"] == "FORBIDDEN"

    patched = api_client.patch(
        f"/api/v1/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "deactivated"},
    )
    assert patched.status_code == 200
    assert patched.json()["data"]["status"] == "deactivated"


def test_duplicate_identifier_conflict(api_client: TestClient) -> None:
    token = _login(api_client, "admin")
    response = api_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "identifier": "Admin",
            "display_name": "Dup",
            "password": "abcdefghijkl",
            "role": "Viewer",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ACCOUNT_CONFLICT"
