"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError, ProgrammingError, SQLAlchemyError

from app.api.admin_users import router as admin_users_router
from app.api.auth import router as auth_router
from app.api.errors import install_exception_handlers
from app.api.health import router as health_router
from app.core.config import Settings, get_settings
from app.domain.identity import AuthError
from app.repositories.database import configure_engine, get_engine, get_session_factory
from app.repositories.readiness_repository import ReadinessRepository
from app.services.bootstrap_service import BootstrapService
from app.services.health_service import HealthService


def _validate_jwt_settings(settings: Settings) -> None:
    if settings.app_env != "local" and not str(settings.jwt_signing_key or "").strip():
        raise AuthError("AUTH_INTERNAL_ERROR", "JWT signing key is not configured.", 500)


def _run_bootstrap(settings: Settings) -> None:
    if not settings.auth_bootstrap_on_startup:
        return
    try:
        BootstrapService(get_session_factory()).run()
    except (OperationalError, ProgrammingError):
        # Database or users table not ready yet; readiness probe remains authoritative.
        return


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or get_settings()
    configure_engine(resolved.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        _validate_jwt_settings(app.state.settings)
        try:
            _run_bootstrap(app.state.settings)
        except AuthError:
            # Fail closed when zero Admins exist and bootstrap config is missing/invalid.
            raise
        yield

    app = FastAPI(title="Quarry KB API", version="0.1.0", lifespan=lifespan)
    app.state.settings = resolved
    app.state.health_service = HealthService(
        settings=resolved,
        repository_factory=lambda: ReadinessRepository(
            engine=get_engine(),
            expected_revision=resolved.expected_alembic_revision,
        ),
    )
    install_exception_handlers(app)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(admin_users_router, prefix="/api/v1")
    return app


app = create_app()
