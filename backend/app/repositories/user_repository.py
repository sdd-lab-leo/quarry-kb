"""User persistence repository."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import Select, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.identity import AuthError, UserRole, UserStatus
from app.models.user import User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)

    def get_by_identifier(self, identifier: str) -> User | None:
        stmt: Select[tuple[User]] = select(User).where(User.identifier == identifier)
        return self._session.scalars(stmt).first()

    def list_users(self, limit: int = 200) -> list[User]:
        stmt = select(User).order_by(User.created_at.asc()).limit(limit)
        return list(self._session.scalars(stmt).all())

    def count_admins(self, *, for_update: bool = False) -> int:
        stmt = select(func.count()).select_from(User).where(User.role == UserRole.ADMIN.value)
        if for_update:
            stmt = stmt.with_for_update()
        return int(self._session.scalar(stmt) or 0)

    def count_active_admins(self, *, for_update: bool = False) -> int:
        stmt = (
            select(func.count())
            .select_from(User)
            .where(User.role == UserRole.ADMIN.value, User.status == UserStatus.ACTIVE.value)
        )
        if for_update:
            stmt = stmt.with_for_update()
        return int(self._session.scalar(stmt) or 0)

    def create(
        self,
        *,
        identifier: str,
        display_name: str,
        role: UserRole,
        password_hash: str,
        status: UserStatus = UserStatus.ACTIVE,
    ) -> User:
        now = datetime.now(UTC)
        user = User(
            user_id=uuid.uuid4(),
            identifier=identifier,
            display_name=display_name,
            role=role.value,
            status=status.value,
            password_hash=password_hash,
            external_subject=None,
            auth_version=0,
            created_at=now,
            updated_at=now,
            deactivated_at=None,
        )
        self._session.add(user)
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise AuthError("ACCOUNT_CONFLICT", "Account identifier already exists.", 409) from exc
        return user

    def save(self, user: User) -> User:
        user.updated_at = datetime.now(UTC)
        self._session.add(user)
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise AuthError("ACCOUNT_CONFLICT", "Account identifier already exists.", 409) from exc
        return user
