"""Auth migration contract tests (no live database required)."""

from __future__ import annotations

from pathlib import Path

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20260726_0002_create_users.py"
)


def test_users_migration_extends_baseline_only() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "20260726_0002"' in text
    assert 'down_revision: Union[str, None] = "20260726_0001"' in text
    assert 'op.create_table(\n        "users"' in text or 'op.create_table(\n        "users",' in text
    assert "password_hash" in text
    assert "auth_version" in text
    assert "external_subject" in text
    for marker in ("documents", "chunks", "sessions", "messages", "citations", "audit", "providers"):
        assert marker not in text.lower() or marker in "external_subject"
    assert "documents" not in text
    assert "audit" not in text
    assert "chunks" not in text
