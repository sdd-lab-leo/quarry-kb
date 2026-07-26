"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from app.core.config import reset_settings_cache
from app.repositories.database import reset_engine


@pytest.fixture(autouse=True)
def _clean_settings(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("GATEWAY_HOST_ALLOWLIST", "gateway.internal")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("OCR_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("CHAT_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("UPLOAD_ROOT", "/tmp/quarry-uploads")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://quarry:change-me-local-only@localhost:5432/quarry_kb",
    )
    monkeypatch.setenv("JWT_SIGNING_KEY", "test-signing-key-not-for-production")
    monkeypatch.setenv("AUTH_BOOTSTRAP_ON_STARTUP", "false")
    reset_settings_cache()
    reset_engine()
    yield
    reset_settings_cache()
    reset_engine()
