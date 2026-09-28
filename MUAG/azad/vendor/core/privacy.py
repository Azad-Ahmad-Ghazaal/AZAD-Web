from __future__ import annotations

import re


_PATTERNS = (
    re.compile(r"(?i)(api[_ -]?key|token|secret|password)\s*[:=]\s*['\"]?[^\s'\"]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]{12,}"),
    re.compile(r"\b(?:sk|pk)_[A-Za-z0-9_-]{16,}\b"),
)


def redact_sensitive(text: str) -> str:
    """Remove common credential-shaped values before persistent logging/context export."""
    value = str(text or "")
    for pattern in _PATTERNS:
        value = pattern.sub("[REDACTED]", value)
    return value


def contains_sensitive_shape(text: str) -> bool:
    value = str(text or "")
    return any(pattern.search(value) for pattern in _PATTERNS)


__all__ = ["redact_sensitive", "contains_sensitive_shape"]
