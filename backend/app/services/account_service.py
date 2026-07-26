"""Admin account lifecycle service."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.adapters.password_adapter import PasswordAdapter
from app.domain.identity import (
    AuthError,
    UserRole,
    UserStatus,
    validate_display_name,
    validate_identifier,
    validate_password_policy,
    validate_role,
    validate_status,
)
from app.repositories.user_repository import UserRepository
from app.services.user_projection import user_summary


class AccountService:
    def __init__(self, users: UserRepository, passwords: PasswordAdapter) -> None:
        self._users = users
        self._passwords = passwords

    def list_users(self) -> dict:
        items = [user_summary(user) for user in self._users.list_users(limit=200)]
        return {"items": items}

    def create_user(self, *, identifier: str, display_name: str, password: str, role: str) -> dict:
        normalized = validate_identifier(identifier)
        name = validate_display_name(display_name)
        validate_password_policy(password)
        role_value = validate_role(role)
        if self._users.get_by_identifier(normalized) is not None:
            raise AuthError("ACCOUNT_CONFLICT", "Account identifier already exists.", 409)
        user = self._users.create(
            identifier=normalized,
            display_name=name,
            role=role_value,
            password_hash=self._passwords.hash(password),
        )
        return user_summary(user)

    def update_user(
        self,
        user_id: UUID,
        *,
        display_name: str | None = None,
        role: str | None = None,
        status: str | None = None,
    ) -> dict:
        if display_name is None and role is None and status is None:
            raise AuthError("VALIDATION_ERROR", "At least one field is required.", 422)

        # Serialize competing Admin mutations.
        self._users.count_active_admins(for_update=True)
        user = self._users.get_by_id(user_id)
        if user is None:
            raise AuthError("USER_NOT_FOUND", "User was not found.", 404)

        next_display = validate_display_name(display_name) if display_name is not None else user.display_name
        next_role = validate_role(role) if role is not None else UserRole(user.role)
        next_status = validate_status(status) if status is not None else UserStatus(user.status)

        self._assert_last_admin_safe(user, next_role=next_role, next_status=next_status)

        user.display_name = next_display
        user.role = next_role.value

        if next_status == UserStatus.DEACTIVATED and user.status != UserStatus.DEACTIVATED.value:
            user.status = UserStatus.DEACTIVATED.value
            user.deactivated_at = datetime.now(UTC)
            user.auth_version += 1
        elif next_status == UserStatus.ACTIVE and user.status != UserStatus.ACTIVE.value:
            user.status = UserStatus.ACTIVE.value
            user.deactivated_at = None
        else:
            user.status = next_status.value

        self._users.save(user)
        return user_summary(user)

    def _assert_last_admin_safe(self, user, *, next_role: UserRole, next_status: UserStatus) -> None:
        is_active_admin = user.role == UserRole.ADMIN.value and user.status == UserStatus.ACTIVE.value
        if not is_active_admin:
            return
        remains_active_admin = next_role == UserRole.ADMIN and next_status == UserStatus.ACTIVE
        if remains_active_admin:
            return
        if self._users.count_active_admins(for_update=True) <= 1:
            raise AuthError(
                "LAST_ADMIN_REQUIRED",
                "The last active Admin cannot be deactivated or demoted.",
                409,
            )
