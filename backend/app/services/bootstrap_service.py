"""First-Admin bootstrap from runtime environment variables."""

from __future__ import annotations

import os

from sqlalchemy.orm import Session, sessionmaker

from app.adapters.password_adapter import PasswordAdapter
from app.domain.identity import (
    AuthError,
    UserRole,
    validate_display_name,
    validate_identifier,
    validate_password_policy,
)
from app.repositories.user_repository import UserRepository


class BootstrapService:
    def __init__(
        self,
        session_factory: sessionmaker[Session],
        passwords: PasswordAdapter | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._passwords = passwords or PasswordAdapter()

    def run(self) -> None:
        with self._session_factory() as session:
            users = UserRepository(session)
            # Serialize zero-Admin check/create.
            admin_count = users.count_admins(for_update=True)
            if admin_count > 0:
                session.commit()
                return

            identifier = os.environ.get("AUTH_BOOTSTRAP_ADMIN_IDENTIFIER")
            password = os.environ.get("AUTH_BOOTSTRAP_ADMIN_PASSWORD")
            display_name_raw = os.environ.get("AUTH_BOOTSTRAP_ADMIN_DISPLAY_NAME")

            if not identifier or not password:
                session.rollback()
                raise AuthError(
                    "AUTH_INTERNAL_ERROR",
                    "Bootstrap Admin configuration is missing.",
                    500,
                )

            try:
                normalized = validate_identifier(identifier)
                validate_password_policy(password)
                display_name = (
                    validate_display_name(display_name_raw)
                    if display_name_raw
                    else validate_display_name(normalized)
                )
            except AuthError as exc:
                session.rollback()
                raise AuthError(
                    "AUTH_INTERNAL_ERROR",
                    "Bootstrap Admin configuration is invalid.",
                    500,
                ) from exc

            try:
                users.create(
                    identifier=normalized,
                    display_name=display_name,
                    role=UserRole.ADMIN,
                    password_hash=self._passwords.hash(password),
                )
                session.commit()
            except AuthError as exc:
                session.rollback()
                # Concurrent bootstrap losers may observe a unique conflict after the winner commits.
                if exc.code == "ACCOUNT_CONFLICT" and users.count_admins() >= 1:
                    session.commit()
                    return
                raise
