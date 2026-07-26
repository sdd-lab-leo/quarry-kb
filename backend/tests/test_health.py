"""Liveness and readiness API tests."""

from __future__ import annotations

from dataclasses import dataclass

from fastapi.testclient import TestClient

from app.core.config import Settings, reset_settings_cache
from app.main import create_app
from app.repositories.readiness_repository import ComponentCheck, ReadinessRepository
from app.services.health_service import HealthService


@dataclass
class FakeRepo:
    database: ComponentCheck
    migration: ComponentCheck
    vector: ComponentCheck

    def check_database(self) -> ComponentCheck:
        return self.database

    def check_migration(self) -> ComponentCheck:
        return self.migration

    def check_vector_capability(self) -> ComponentCheck:
        return self.vector


def _client_with_repo(repo: FakeRepo, settings: Settings | None = None) -> TestClient:
    reset_settings_cache()
    app = create_app()
    resolved = settings or Settings()
    app.state.settings = resolved
    app.state.health_service = HealthService(
        settings=resolved,
        repository_factory=lambda: repo,  # type: ignore[arg-type,return-value]
    )
    return TestClient(app)


def test_liveness_does_not_require_database() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(False, "down"),
            migration=ComponentCheck(False, "missing"),
            vector=ComponentCheck(False, "missing"),
        )
    )
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "alive"


def test_readiness_ready_returns_200() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(True),
            migration=ComponentCheck(True),
            vector=ComponentCheck(True),
        )
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "ready"
    assert body["data"]["components"] == {
        "configuration": "ready",
        "database": "ready",
        "migration": "ready",
        "vector_capability": "ready",
    }
    assert body["error"] is None


def test_readiness_database_unavailable_returns_503() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(False, "Database connection unavailable."),
            migration=ComponentCheck(False, "ignored"),
            vector=ComponentCheck(False, "ignored"),
        )
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["success"] is False
    assert body["data"]["status"] == "not_ready"
    assert body["data"]["components"]["configuration"] == "ready"
    assert body["data"]["components"]["database"] == "not_ready"
    assert body["error"]["code"] == "DATABASE_NOT_READY"


def test_readiness_migration_pending_returns_503() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(True),
            migration=ComponentCheck(False, "Baseline migration is missing."),
            vector=ComponentCheck(False, "ignored"),
        )
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "MIGRATION_NOT_CURRENT"
    assert response.json()["data"]["components"]["database"] == "ready"
    assert response.json()["data"]["components"]["migration"] == "not_ready"


def test_readiness_vector_unavailable_returns_503() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(True),
            migration=ComponentCheck(True),
            vector=ComponentCheck(False, "PostgreSQL vector extension is unavailable."),
        )
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "VECTOR_CAPABILITY_UNAVAILABLE"
    assert response.json()["data"]["components"]["vector_capability"] == "not_ready"


def test_readiness_invalid_config_returns_503(monkeypatch) -> None:
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")
    reset_settings_cache()
    settings = Settings()
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(True),
            migration=ComponentCheck(True),
            vector=ComponentCheck(True),
        ),
        settings=settings,
    )
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["error"]["code"] == "CONFIGURATION_INVALID"
    assert body["data"]["components"]["configuration"] == "not_ready"


def test_readiness_response_does_not_include_gateway_health() -> None:
    client = _client_with_repo(
        FakeRepo(
            database=ComponentCheck(True),
            migration=ComponentCheck(True),
            vector=ComponentCheck(True),
        )
    )
    body = client.get("/api/v1/health/ready").json()
    components = body["data"]["components"]
    assert "gateway" not in components
    assert "chat" not in components
    assert "embedding" not in components
    assert "ocr" not in components


def test_readiness_repository_type_hint_compatible() -> None:
    # Sanity: production factory uses the real repository class.
    assert hasattr(ReadinessRepository, "check_vector_capability")
