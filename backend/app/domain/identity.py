"""Identity domain constants and validation helpers."""

from __future__ import annotations

import re
from enum import Enum

IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9._@-]+$")
IDENTIFIER_MIN = 3
IDENTIFIER_MAX = 64
DISPLAY_NAME_MIN = 1
DISPLAY_NAME_MAX = 128
PASSWORD_MIN = 12


class UserRole(str, Enum):
    ADMIN = "Admin"
    EDITOR = "Editor"
    VIEWER = "Viewer"


class UserStatus(str, Enum):
    ACTIVE = "active"
    DEACTIVATED = "deactivated"


class AuthError(Exception):
    def __init__(self, code: str, message: str, http_status: int) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


def normalize_identifier(raw: str) -> str:
    return raw.strip().lower()


def validate_identifier(raw: str) -> str:
    normalized = normalize_identifier(raw)
    if not (IDENTIFIER_MIN <= len(normalized) <= IDENTIFIER_MAX):
        raise AuthError("VALIDATION_ERROR", "Identifier is invalid.", 422)
    if not IDENTIFIER_PATTERN.fullmatch(normalized):
        raise AuthError("VALIDATION_ERROR", "Identifier is invalid.", 422)
    return normalized


def validate_display_name(raw: str) -> str:
    value = raw.strip()
    if not (DISPLAY_NAME_MIN <= len(value) <= DISPLAY_NAME_MAX):
        raise AuthError("VALIDATION_ERROR", "Display name is invalid.", 422)
    return value


def validate_password_policy(password: str) -> None:
    if len(password) < PASSWORD_MIN or password.strip() == "":
        raise AuthError("VALIDATION_ERROR", "Password does not meet policy.", 422)
    if not any(not ch.isspace() for ch in password):
        raise AuthError("VALIDATION_ERROR", "Password does not meet policy.", 422)


def validate_role(raw: str) -> UserRole:
    try:
        return UserRole(raw)
    except ValueError as exc:
        raise AuthError("VALIDATION_ERROR", "Role is invalid.", 422) from exc


def validate_status(raw: str) -> UserStatus:
    try:
        return UserStatus(raw)
    except ValueError as exc:
        raise AuthError("VALIDATION_ERROR", "Status is invalid.", 422) from exc
