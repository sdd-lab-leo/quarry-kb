"""Secret-safe diagnostic helpers."""

from __future__ import annotations

import re

_SENSITIVE_PATTERNS = [
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*\S+"),
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*[:=]\s*\S+"),
    re.compile(r"(?i)authorization\s*[:=]\s*\S+(?:\s+\S+)?"),
    re.compile(r"(?i)://[^/\s:]+:[^/@\s]+@"),
    re.compile(r"(?i)\bbearer\s+[a-z0-9\-\._~\+/]+=*"),
]


def redact_text(value: str) -> str:
    redacted = value
    for pattern in _SENSITIVE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted


def safe_error_message(exc: BaseException, fallback: str) -> str:
    text = redact_text(str(exc)).strip()
    if not text:
        return fallback
    # Avoid leaking long/raw exception bodies in probe responses.
    if len(text) > 160 or "Traceback" in text:
        return fallback
    return text
