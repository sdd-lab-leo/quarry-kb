"""HS256 JWT adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import jwt

from app.domain.identity import AuthError

ALGORITHM = "HS256"
ACCESS_TOKEN_TTL = timedelta(minutes=30)


class JwtAdapter:
    def __init__(self, signing_key: str) -> None:
        if not signing_key or not signing_key.strip():
            raise AuthError("AUTH_INTERNAL_ERROR", "JWT signing key is not configured.", 500)
        self._signing_key = signing_key

    def issue(self, user_id: UUID, auth_version: int, now: datetime | None = None) -> tuple[str, datetime]:
        issued_at = now or datetime.now(UTC)
        if issued_at.tzinfo is None:
            issued_at = issued_at.replace(tzinfo=UTC)
        expires_at = issued_at + ACCESS_TOKEN_TTL
        payload = {
            "sub": str(user_id),
            "iat": int(issued_at.timestamp()),
            "exp": int(expires_at.timestamp()),
            "auth_version": int(auth_version),
        }
        token = jwt.encode(payload, self._signing_key, algorithm=ALGORITHM)
        return token, expires_at

    def verify(self, token: str, now: datetime | None = None) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self._signing_key,
                algorithms=[ALGORITHM],
                options={"require": ["sub", "iat", "exp"]},
            )
        except jwt.PyJWTError as exc:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401) from exc

        if "auth_version" not in claims:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)
        try:
            auth_version = int(claims["auth_version"])
            user_id = UUID(str(claims["sub"]))
        except (TypeError, ValueError) as exc:
            raise AuthError("TOKEN_INVALID", "Token is invalid.", 401) from exc

        if now is not None:
            # PyJWT already checks exp against wall clock; explicit now used in tests via monkeypatch if needed.
            exp = int(claims["exp"])
            if int(now.timestamp()) >= exp:
                raise AuthError("TOKEN_INVALID", "Token is invalid.", 401)

        return {"user_id": user_id, "auth_version": auth_version, "exp": int(claims["exp"]), "iat": int(claims["iat"])}
