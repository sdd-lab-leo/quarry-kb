"""Secret redaction tests."""

from __future__ import annotations

from app.core.redaction import redact_text, safe_error_message


def test_redact_password_and_token() -> None:
    text = "password=super-secret api_key=abcd Authorization: Bearer xyz"
    redacted = redact_text(text)
    assert "super-secret" not in redacted
    assert "abcd" not in redacted
    assert "xyz" not in redacted
    assert "[REDACTED]" in redacted


def test_redact_connection_string_credentials() -> None:
    text = "postgresql://quarry:change-me-local-only@postgres:5432/quarry_kb"
    redacted = redact_text(text)
    assert "change-me-local-only" not in redacted
    assert "[REDACTED]" in redacted


def test_safe_error_message_falls_back_for_traceback() -> None:
    class Boom(Exception):
        def __str__(self) -> str:
            return "Traceback (most recent call last):\npassword=secret"

    assert safe_error_message(Boom(), "Database is not ready.") == "Database is not ready."
