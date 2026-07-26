"""FastAPI dependencies for auth."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.adapters.jwt_adapter import JwtAdapter
from app.adapters.password_adapter import PasswordAdapter
from app.domain.identity import AuthError, UserRole
from app.repositories.database import get_session_factory
from app.repositories.user_repository import UserRepository
from app.services.account_service import AccountService
from app.services.auth_service import AuthenticatedUser, AuthService


def db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def password_adapter() -> PasswordAdapter:
    return PasswordAdapter()


def jwt_adapter(request: Request) -> JwtAdapter:
    settings = request.app.state.settings
    key = getattr(settings, "jwt_signing_key", "") or ""
    if (settings.app_env != "local") and not str(key).strip():
        raise AuthError("AUTH_INTERNAL_ERROR", "JWT signing key is not configured.", 500)
    if not str(key).strip():
        # local may use a deterministic test/dev key only when explicitly configured empty -> fail closed for issuing
        raise AuthError("AUTH_INTERNAL_ERROR", "JWT signing key is not configured.", 500)
    return JwtAdapter(str(key))


def auth_service(
    session: Session = Depends(db_session),
    passwords: PasswordAdapter = Depends(password_adapter),
    tokens: JwtAdapter = Depends(jwt_adapter),
) -> AuthService:
    return AuthService(UserRepository(session), passwords, tokens)


def account_service(
    session: Session = Depends(db_session),
    passwords: PasswordAdapter = Depends(password_adapter),
) -> AccountService:
    return AccountService(UserRepository(session), passwords)


def require_active_user(
    request: Request,
    service: AuthService = Depends(auth_service),
) -> AuthenticatedUser:
    return service.resolve_bearer(request.headers.get("Authorization"))


def require_admin(user: AuthenticatedUser = Depends(require_active_user)) -> AuthenticatedUser:
    if user.role != UserRole.ADMIN:
        raise AuthError("FORBIDDEN", "Admin role is required.", 403)
    return user
