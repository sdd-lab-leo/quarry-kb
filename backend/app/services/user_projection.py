"""Safe UserSummary projection."""

from __future__ import annotations

from typing import Any

from app.models.user import User


def user_summary(user: User) -> dict[str, Any]:
    return {
        "user_id": str(user.user_id),
        "identifier": user.identifier,
        "display_name": user.display_name,
        "role": user.role,
        "status": user.status,
        "created_at": _iso(user.created_at),
        "updated_at": _iso(user.updated_at),
    }


def _iso(value: Any) -> str:
    if value is None:
        return ""
    if getattr(value, "tzinfo", None) is None:
        return value.isoformat() + "Z"
    return value.astimezone().isoformat().replace("+00:00", "Z")
