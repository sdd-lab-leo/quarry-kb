"""Create users table for auth-password-jwt.

Revision ID: 20260726_0002
Revises: 20260726_0001
Create Date: 2026-07-26
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260726_0002"
down_revision: Union[str, None] = "20260726_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Uuid(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("identifier", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("external_subject", sa.String(length=255), nullable=True),
        sa.Column("auth_version", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("deactivated_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("role IN ('Admin', 'Editor', 'Viewer')", name="ck_users_role"),
        sa.CheckConstraint("status IN ('active', 'deactivated')", name="ck_users_status"),
        sa.UniqueConstraint("identifier", name="uq_users_identifier"),
    )
    op.create_index("ix_users_status", "users", ["status"])
    op.create_index(
        "uq_users_external_subject",
        "users",
        ["external_subject"],
        unique=True,
        postgresql_where=sa.text("external_subject IS NOT NULL"),
        sqlite_where=sa.text("external_subject IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_users_external_subject", table_name="users")
    op.drop_index("ix_users_status", table_name="users")
    op.drop_table("users")
