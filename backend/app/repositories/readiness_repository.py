"""Read-only readiness checks against PostgreSQL/Alembic state."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError


@dataclass(frozen=True)
class ComponentCheck:
    ready: bool
    detail: str = ""


class ReadinessRepository:
    def __init__(self, engine: Engine, expected_revision: str) -> None:
        self._engine = engine
        self._expected_revision = expected_revision

    def check_database(self) -> ComponentCheck:
        try:
            with self._engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return ComponentCheck(ready=True)
        except SQLAlchemyError:
            return ComponentCheck(ready=False, detail="Database connection unavailable.")

    def check_migration(self) -> ComponentCheck:
        try:
            with self._engine.connect() as conn:
                exists = conn.execute(
                    text("SELECT to_regclass('public.alembic_version') IS NOT NULL")
                ).scalar()
                if not exists:
                    return ComponentCheck(ready=False, detail="Baseline migration is missing.")
                current = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
                if current != self._expected_revision:
                    return ComponentCheck(
                        ready=False,
                        detail="Baseline migration is not current.",
                    )
            return ComponentCheck(ready=True)
        except SQLAlchemyError:
            return ComponentCheck(ready=False, detail="Migration state unavailable.")

    def check_vector_capability(self) -> ComponentCheck:
        try:
            with self._engine.connect() as conn:
                present = conn.execute(
                    text("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                ).scalar()
                if not present:
                    return ComponentCheck(
                        ready=False,
                        detail="PostgreSQL vector extension is unavailable.",
                    )
            return ComponentCheck(ready=True)
        except SQLAlchemyError:
            return ComponentCheck(ready=False, detail="Vector capability check failed.")
