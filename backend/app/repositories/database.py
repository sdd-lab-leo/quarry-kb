"""SQLAlchemy engine/session helpers."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def build_engine(database_url: str) -> Engine:
    return create_engine(database_url, pool_pre_ping=True, future=True)


def configure_engine(database_url: str) -> Engine:
    global _engine, _session_factory
    _engine = build_engine(database_url)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def get_engine() -> Engine:
    if _engine is None:
        raise RuntimeError("Database engine is not configured.")
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    if _session_factory is None:
        raise RuntimeError("Database session factory is not configured.")
    return _session_factory


def reset_engine() -> None:
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def session_dependency() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
