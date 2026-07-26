"""Configuration parsing and allowlist tests."""

from __future__ import annotations

import pytest

from app.core.config import (
    Settings,
    SettingsError,
    assert_host_allowlisted,
    extract_url_host,
    parse_allowlist,
)


def test_parse_allowlist_splits_and_normalizes() -> None:
    assert parse_allowlist("gateway.internal, Gateway.Example:8443") == {
        "gateway.internal",
        "gateway.example:8443",
    }


def test_parse_allowlist_rejects_empty() -> None:
    with pytest.raises(SettingsError) as exc:
        parse_allowlist(" , ")
    assert exc.value.code == "CONFIGURATION_INVALID"


def test_extract_url_host_literal() -> None:
    assert extract_url_host("https://gateway.internal/v1/embeddings") == "gateway.internal"
    assert extract_url_host("http://gateway.internal:8080/ocr") == "gateway.internal:8080"


def test_extract_url_host_rejects_empty() -> None:
    with pytest.raises(SettingsError):
        extract_url_host("")


def test_allowlist_accepts_listed_host() -> None:
    host = assert_host_allowlisted(
        "http://gateway.internal/v1",
        {"gateway.internal"},
        "EMBEDDING_BASE_URL",
    )
    assert host == "gateway.internal"


def test_allowlist_rejects_public_host() -> None:
    with pytest.raises(SettingsError) as exc:
        assert_host_allowlisted(
            "https://api.openai.com/v1",
            {"gateway.internal"},
            "EMBEDDING_BASE_URL",
        )
    assert "not on GATEWAY_HOST_ALLOWLIST" in exc.value.message


def test_allowlist_rejects_unlisteds_even_if_looks_private() -> None:
    with pytest.raises(SettingsError):
        assert_host_allowlisted(
            "http://10.0.0.5/v1",
            {"gateway.internal"},
            "OCR_BASE_URL",
        )


def test_settings_validate_for_readiness_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEWAY_HOST_ALLOWLIST", "gateway.internal")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("OCR_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("CHAT_BASE_URL", "http://gateway.internal/v1")
    monkeypatch.setenv("UPLOAD_ROOT", "/data/uploads")
    settings = Settings()
    settings.validate_for_readiness()


def test_settings_validate_rejects_public_embedding(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GATEWAY_HOST_ALLOWLIST", "gateway.internal")
    monkeypatch.setenv("EMBEDDING_BASE_URL", "https://public.example/v1")
    monkeypatch.setenv("OCR_BASE_URL", "http://gateway.internal/v1")
    settings = Settings()
    with pytest.raises(SettingsError) as exc:
        settings.validate_for_readiness()
    assert exc.value.code == "CONFIGURATION_INVALID"
