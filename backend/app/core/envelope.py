"""Stable API response envelope helpers."""

from __future__ import annotations

from typing import Any


def success_envelope(data: dict[str, Any], meta: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"success": True, "data": data, "error": None, "meta": meta}


def error_envelope(
    *,
    data: dict[str, Any] | None,
    code: str,
    message: str,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "success": False,
        "data": data,
        "error": {"code": code, "message": message},
        "meta": meta,
    }
