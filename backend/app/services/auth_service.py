"""Authentication and current-user services."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.adapters.jwt_adapter import JwtAdapter
from app.adapters.password_adapter import PasswordAdapter
from app.domain.identity import (
    AuthError,
    UserRole,
    UserStatus,
    normalize_identifier,
    validate_identifier,
)
from app.repositories.user_repository import UserRepository
from app.services.user_projection import user_summary


@dataclass(frozen=True)
class AuthenticatedUser:
    user_id: UUID
    role: UserRole
    status: UserStatus
    auth_version: int


class AuthService:
    def __init__(
        self,
        users: UserRepository,
        passwords: PasswordAdapter,
        tokens: JwtAdapter,
    ) -> None:
        self._users = users
        self._passwords = passwords
        self._tokens = tokens

    def login(self, identifier: str, password: str) -> dict:
        # Request-shape / identifier format failures are validation.
        # Structurally valid credential mismatches are generic auth failures.
        try:
            normalized = validate_identifier(identifier)
        except AuthError:
            # Empty / invalid shape already raised; re-raise validation.
            if not identifier or not str(identifier).strip():
                raise
            # If identifier fails pattern/length, treat as validation.
            raise

        if password is None or password == "":
            raise AuthError("VALIDATION_ERROR", "Password is required.", 422)

        user = self._users.get_by_identifier(normalized)
        if user is None or user.status != UserStatus.ACTIVE.value:
            raise AuthError("AUTHENTICATION_FAILED", "Invalid credentials.", 401)
        if not self._passwords.verify(password, user.password_hash):
            raise AuthError("AUTHENTICATION_FAILED", "Invalid credentials.", 401)

        token, expires_at = self._tokens.issue(user.user_id, user.auth_version)
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_at": expires_at.astimezone(UTC).isoformat().replace("+00:00", "Z"),
            "user": user_summary(user),
        }

    def resolve_bearer(self, authorization: str | None) -> AuthenticatedUser:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)
        token = authorization.split(" ", 1)[1].strip()
        if not token:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)
        claims = self._tokens.verify(token)
        user = self._users.get_by_id(claims["user_id"])
        if user is None:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)
        if user.status != UserStatus.ACTIVE.value or user.auth_version != claims["auth_version"]:
            raise AuthError("ACCOUNT_INACTIVE", "Account is inactive.", 401)
        return AuthenticatedUser(
            user_id=user.user_id,
            role=UserRole(user.role),
            status=UserStatus(user.status),
            auth_version=user.auth_version,
        )

    def current_user_summary(self, auth: AuthenticatedUser) -> dict:
        user = self._users.get_by_id(auth.user_id)
        if user is None:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)
        return user_summary(user)
