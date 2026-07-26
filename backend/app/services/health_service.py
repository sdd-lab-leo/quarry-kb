"""Liveness and readiness orchestration. Never calls model gateways."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.core.config import Settings, SettingsError
from app.repositories.readiness_repository import ReadinessRepository

ComponentState = str  # "ready" | "not_ready"


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    status: str
    components: dict[str, ComponentState]
    error_code: str | None
    error_message: str | None


class HealthService:
    def __init__(
        self,
        settings: Settings,
        repository_factory: Callable[[], ReadinessRepository],
    ) -> None:
        self._settings = settings
        self._repository_factory = repository_factory

    def liveness(self) -> dict[str, str]:
        return {"status": "alive"}

    def readiness(self) -> ReadinessResult:
        components: dict[str, ComponentState] = {
            "configuration": "not_ready",
            "database": "not_ready",
            "migration": "not_ready",
            "vector_capability": "not_ready",
        }

        try:
            self._settings.validate_for_readiness()
            components["configuration"] = "ready"
        except SettingsError as exc:
            return ReadinessResult(
                ready=False,
                status="not_ready",
                components=components,
                error_code=exc.code,
                error_message=exc.message,
            )

        repository = self._repository_factory()
        db_check = repository.check_database()
        if not db_check.ready:
            return ReadinessResult(
                ready=False,
                status="not_ready",
                components=components,
                error_code="DATABASE_NOT_READY",
                error_message=db_check.detail or "Database is not ready.",
            )
        components["database"] = "ready"

        migration_check = repository.check_migration()
        if not migration_check.ready:
            return ReadinessResult(
                ready=False,
                status="not_ready",
                components=components,
                error_code="MIGRATION_NOT_CURRENT",
                error_message=migration_check.detail or "Migration is not current.",
            )
        components["migration"] = "ready"

        vector_check = repository.check_vector_capability()
        if not vector_check.ready:
            return ReadinessResult(
                ready=False,
                status="not_ready",
                components=components,
                error_code="VECTOR_CAPABILITY_UNAVAILABLE",
                error_message=vector_check.detail or "Vector capability is unavailable.",
            )
        components["vector_capability"] = "ready"

        return ReadinessResult(
            ready=True,
            status="ready",
            components=components,
            error_code=None,
            error_message=None,
        )
