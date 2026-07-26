"""Typed settings and embedding/OCR host allowlist validation."""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SettingsError(ValueError):
    """Raised when configuration is invalid for readiness."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(message)


def parse_allowlist(raw: str) -> set[str]:
    hosts = {item.strip().lower() for item in raw.split(",") if item.strip()}
    if not hosts:
        raise SettingsError("CONFIGURATION_INVALID", "GATEWAY_HOST_ALLOWLIST must not be empty.")
    return hosts


def extract_url_host(url: str) -> str:
    if not url or not url.strip():
        raise SettingsError("CONFIGURATION_INVALID", "Embedding/OCR URL must not be empty.")
    parsed = urlparse(url.strip())
    if not parsed.scheme or not parsed.netloc:
        raise SettingsError("CONFIGURATION_INVALID", "Embedding/OCR URL must include scheme and host.")
    host = parsed.netloc.lower()
    # Strip userinfo if present without echoing secrets.
    if "@" in host:
        host = host.rsplit("@", 1)[-1]
    return host


def assert_host_allowlisted(url: str, allowlist: set[str], label: str) -> str:
    """Validate URL host by literal hostname or host:port match. No DNS lookup."""
    host = extract_url_host(url)
    if host not in allowlist:
        raise SettingsError(
            "CONFIGURATION_INVALID",
            f"{label} host is not on GATEWAY_HOST_ALLOWLIST.",
        )
    return host


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "local"
    log_level: str = "INFO"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    database_url: str = Field(
        default="postgresql+psycopg://quarry:change-me-local-only@localhost:5432/quarry_kb"
    )
    upload_root: str = "/data/uploads"

    gateway_host_allowlist: str = "gateway.internal"

    chat_base_url: str = "http://gateway.internal/v1"
    chat_model: str = "placeholder-chat-model"
    chat_api_key: str = "replace-me"

    embedding_base_url: str = "http://gateway.internal/v1"
    embedding_model: str = "placeholder-embedding-model"
    embedding_dimension: int = 1536
    embedding_api_key: str = "replace-me"

    ocr_base_url: str = "http://gateway.internal/v1"
    ocr_model_path: str = "/v1/ocr"
    ocr_timeout_seconds: int = 120
    ocr_api_key: str = "replace-me"

    alembic_config_path: str = "alembic.ini"
    expected_alembic_revision: str = "20260726_0002"

    jwt_signing_key: str = ""
    auth_bootstrap_on_startup: bool = True

    @field_validator("database_url")
    @classmethod
    def database_url_must_be_present(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("DATABASE_URL must not be empty.")
        return value.strip()

    @property
    def allowlist_hosts(self) -> set[str]:
        return parse_allowlist(self.gateway_host_allowlist)

    def validate_for_readiness(self) -> None:
        """Validate settings required for readiness. Never performs outbound calls."""
        if not self.upload_root.strip():
            raise SettingsError("CONFIGURATION_INVALID", "UPLOAD_ROOT must not be empty.")
        if self.embedding_dimension <= 0:
            raise SettingsError("CONFIGURATION_INVALID", "EMBEDDING_DIMENSION must be positive.")
        if self.ocr_timeout_seconds <= 0:
            raise SettingsError("CONFIGURATION_INVALID", "OCR_TIMEOUT_SECONDS must be positive.")
        allowlist = self.allowlist_hosts
        assert_host_allowlisted(self.embedding_base_url, allowlist, "EMBEDDING_BASE_URL")
        assert_host_allowlisted(self.ocr_base_url, allowlist, "OCR_BASE_URL")
        # Chat remains provider-neutral in bootstrap; public chat is later Admin scope.
        # We still require a parseable placeholder URL for template completeness.
        extract_url_host(self.chat_base_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()


def reset_settings_cache() -> None:
    get_settings.cache_clear()
