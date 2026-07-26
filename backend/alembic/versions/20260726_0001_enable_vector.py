"""Enable PostgreSQL vector extension baseline.

Revision ID: 20260726_0001
Revises:
Create Date: 2026-07-26
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op

revision: str = "20260726_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Foundation-only: enable pgvector capability. No business tables.
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    # Keep extension on downgrade to avoid breaking environments that already rely on it.
    pass
