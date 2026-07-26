"""Argon2id password hashing adapter."""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError


class PasswordAdapter:
    def __init__(self) -> None:
        self._hasher = PasswordHasher()

    def hash(self, plaintext: str) -> str:
        return self._hasher.hash(plaintext)

    def verify(self, plaintext: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, plaintext)
        except (VerifyMismatchError, InvalidHashError, TypeError, ValueError):
            return False
