"""Migration baseline contract tests (no live database required)."""

from __future__ import annotations

from pathlib import Path

MIGRATION = (
    Path(__file__).resolve().parents[1]
    / "alembic"
    / "versions"
    / "20260726_0001_enable_vector.py"
)


def test_baseline_migration_enables_vector_only() -> None:
    text = MIGRATION.read_text(encoding="utf-8")
    assert 'revision: str = "20260726_0001"' in text
    assert "CREATE EXTENSION IF NOT EXISTS vector" in text
    assert "op.create_table" not in text.lower()
    assert "create table" not in text.lower()
    for marker in ("users", "documents", "chunks", "sessions", "messages", "citations", "audit"):
        assert f"create_table('{marker}'" not in text.lower()
