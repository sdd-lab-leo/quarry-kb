"""Unit tests for identity helpers, password/JWT adapters, and auth services."""

from __future__ import annotations

import threading
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.adapters.jwt_adapter import JwtAdapter
from app.adapters.password_adapter import PasswordAdapter
from app.domain.identity import (
    AuthError,
    UserRole,
    UserStatus,
    normalize_identifier,
    validate_identifier,
    validate_password_policy,
)
from app.models import Base, User
from app.repositories.user_repository import UserRepository
from app.services.account_service import AccountService
from app.services.auth_service import AuthService
from app.services.bootstrap_service import BootstrapService


def _session_factory():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def test_identifier_normalization_and_rules() -> None:
    assert normalize_identifier("  Alice@Example.com ") == "alice@example.com"
    assert validate_identifier("  Ab_1 ") == "ab_1"
    with pytest.raises(AuthError) as exc:
        validate_identifier("ab")
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AuthError):
        validate_identifier("Bad Identifier!")


def test_password_policy() -> None:
    validate_password_policy("abcdefghijkl")
    with pytest.raises(AuthError) as exc:
        validate_password_policy("short")
    assert exc.value.code == "VALIDATION_ERROR"
    with pytest.raises(AuthError):
        validate_password_policy("            ")


def test_password_adapter_valid_invalid_and_malformed() -> None:
    adapter = PasswordAdapter()
    hashed = adapter.hash("abcdefghijkl")
    assert adapter.verify("abcdefghijkl", hashed) is True
    assert adapter.verify("wrong-password", hashed) is False
    assert adapter.verify("abcdefghijkl", "not-a-valid-hash") is False


def test_jwt_claims_expiry_and_algorithm() -> None:
    adapter = JwtAdapter("unit-test-signing-key-32-bytes-min!!")
    user_id = uuid.uuid4()
    token, expires_at = adapter.issue(user_id, auth_version=3)
    claims = adapter.verify(token)
    assert claims["user_id"] == user_id
    assert claims["auth_version"] == 3
    assert expires_at > datetime.now(UTC)

    with pytest.raises(AuthError) as exc:
        JwtAdapter("other-key-signing-key-32-bytes-min!!!").verify(token)
    assert exc.value.code == "TOKEN_INVALID"

    with pytest.raises(AuthError):
        JwtAdapter("")


def test_login_generic_failure_and_success() -> None:
    factory = _session_factory()
    passwords = PasswordAdapter()
    tokens = JwtAdapter("unit-test-signing-key-32-bytes-min!!")
    with factory() as session:
        users = UserRepository(session)
        users.create(
            identifier="alice",
            display_name="Alice",
            role=UserRole.VIEWER,
            password_hash=passwords.hash("abcdefghijkl"),
        )
        session.commit()
        service = AuthService(users, passwords, tokens)
        ok = service.login("Alice", "abcdefghijkl")
        assert ok["token_type"] == "bearer"
        assert ok["user"]["identifier"] == "alice"
        assert "password_hash" not in ok["user"]
        with pytest.raises(AuthError) as exc:
            service.login("alice", "wrong-password!!")
        assert exc.value.code == "AUTHENTICATION_FAILED"
        with pytest.raises(AuthError) as exc2:
            service.login("missing", "abcdefghijkl")
        assert exc2.value.code == "AUTHENTICATION_FAILED"

        stored = users.get_by_identifier("alice")
        assert stored is not None
        stored.status = UserStatus.DEACTIVATED.value
        stored.auth_version += 1
        users.save(stored)
        session.commit()
        with pytest.raises(AuthError) as exc3:
            service.login("alice", "abcdefghijkl")
        assert exc3.value.code == "AUTHENTICATION_FAILED"


def test_auth_version_and_role_change_next_request() -> None:
    factory = _session_factory()
    passwords = PasswordAdapter()
    tokens = JwtAdapter("unit-test-signing-key-32-bytes-min!!")
    with factory() as session:
        users = UserRepository(session)
        accounts = AccountService(users, passwords)
        auth = AuthService(users, passwords, tokens)
        users.create(
            identifier="admin",
            display_name="Admin",
            role=UserRole.ADMIN,
            password_hash=passwords.hash("abcdefghijkl"),
        )
        target = users.create(
            identifier="bob",
            display_name="Bob",
            role=UserRole.VIEWER,
            password_hash=passwords.hash("abcdefghijkl"),
        )
        session.commit()
        login = auth.login("bob", "abcdefghijkl")
        bearer = f"Bearer {login['access_token']}"
        resolved = auth.resolve_bearer(bearer)
        assert resolved.role == UserRole.VIEWER

        accounts.update_user(target.user_id, role="Editor")
        session.commit()
        resolved2 = auth.resolve_bearer(bearer)
        assert resolved2.role == UserRole.EDITOR

        accounts.update_user(target.user_id, status="deactivated")
        session.commit()
        with pytest.raises(AuthError) as exc:
            auth.resolve_bearer(bearer)
        assert exc.value.code == "ACCOUNT_INACTIVE"

        accounts.update_user(target.user_id, status="active")
        session.commit()
        with pytest.raises(AuthError) as exc2:
            auth.resolve_bearer(bearer)
        assert exc2.value.code == "ACCOUNT_INACTIVE"


def test_last_admin_protection() -> None:
    factory = _session_factory()
    passwords = PasswordAdapter()
    with factory() as session:
        users = UserRepository(session)
        accounts = AccountService(users, passwords)
        admin = users.create(
            identifier="admin",
            display_name="Admin",
            role=UserRole.ADMIN,
            password_hash=passwords.hash("abcdefghijkl"),
        )
        session.commit()
        with pytest.raises(AuthError) as exc:
            accounts.update_user(admin.user_id, status="deactivated")
        assert exc.value.code == "LAST_ADMIN_REQUIRED"
        with pytest.raises(AuthError) as exc2:
            accounts.update_user(admin.user_id, role="Viewer")
        assert exc2.value.code == "LAST_ADMIN_REQUIRED"


def test_bootstrap_once_and_missing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    factory = _session_factory()
    monkeypatch.delenv("AUTH_BOOTSTRAP_ADMIN_IDENTIFIER", raising=False)
    monkeypatch.delenv("AUTH_BOOTSTRAP_ADMIN_PASSWORD", raising=False)
    with pytest.raises(AuthError) as exc:
        BootstrapService(factory).run()
    assert exc.value.code == "AUTH_INTERNAL_ERROR"

    monkeypatch.setenv("AUTH_BOOTSTRAP_ADMIN_IDENTIFIER", "rootadmin")
    monkeypatch.setenv("AUTH_BOOTSTRAP_ADMIN_PASSWORD", "abcdefghijkl")
    BootstrapService(factory).run()
    BootstrapService(factory).run()  # ignored on repeat
    with factory() as session:
        assert UserRepository(session).count_admins() == 1


def test_bootstrap_concurrent_starts(monkeypatch: pytest.MonkeyPatch) -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    monkeypatch.setenv("AUTH_BOOTSTRAP_ADMIN_IDENTIFIER", "rootadmin")
    monkeypatch.setenv("AUTH_BOOTSTRAP_ADMIN_PASSWORD", "abcdefghijkl")
    errors: list[Exception] = []

    def worker() -> None:
        try:
            BootstrapService(factory).run()
        except Exception as exc:  # noqa: BLE001
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    with factory() as session:
        assert UserRepository(session).count_admins() == 1
    assert errors == []
