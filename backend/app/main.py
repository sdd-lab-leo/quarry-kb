"""FastAPI application entrypoint for repo-bootstrap."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.config import get_settings
from app.repositories.database import configure_engine, get_engine
from app.repositories.readiness_repository import ReadinessRepository
from app.services.health_service import HealthService


def create_app() -> FastAPI:
    settings = get_settings()
    configure_engine(settings.database_url)

    app = FastAPI(title="Quarry KB API", version="0.1.0")
    app.state.settings = settings
    app.state.health_service = HealthService(
        settings=settings,
        repository_factory=lambda: ReadinessRepository(
            engine=get_engine(),
            expected_revision=settings.expected_alembic_revision,
        ),
    )
    app.include_router(health_router, prefix="/api/v1")
    return app


app = create_app()
