"""Internal helpers — ID detection, input validation.

Mirrors guru-cli's validation.ts: defends against agent hallucination patterns
(control chars, path traversal, query/fragment chars, percent-encoding).

Two validation modes:
- validate_input(): For resource IDs, names, structured values (strict).
- validate_free_text(): For natural language — questions, search terms, comments
  (only rejects control chars).
"""

from __future__ import annotations

import re

from guru_sdk.errors import ValidationError

# =============================================================================
# UUID Detection
# =============================================================================

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def is_uuid(value: str) -> bool:
    """Return True if *value* looks like a standard UUID (v1-v5)."""
    return bool(_UUID_RE.match(value))


# =============================================================================
# Input Validation — mirrors guru-cli's validation.ts
# =============================================================================

# Control characters below 0x20 (except tab 0x09, newline 0x0a, CR 0x0d) and DEL 0x7f.
_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Path traversal: ../ or ..\
_PATH_TRAVERSAL_RE = re.compile(r"(?:^|[\\/])\.\.(?:[\\/]|$)")

# Query/fragment characters agents embed inside resource IDs
_QUERY_FRAGMENT_RE = re.compile(r"[?#]")

# Percent-encoded sequences — agents double-encode strings
_PERCENT_ENCODED_RE = re.compile(r"%[0-9a-fA-F]{2}")


def validate_input(value: str, label: str) -> str:
    """Validate a structured input (resource ID, name).

    Rejects control characters, path traversal, query/fragment chars,
    and percent-encoded sequences. Returns *value* unchanged on success.

    Raises:
        ValidationError: If any check fails.
    """
    if not value.strip():
        raise ValidationError(f"{label} must not be empty")

    if _CONTROL_RE.search(value):
        raise ValidationError(f"{label} contains control characters")

    if _PATH_TRAVERSAL_RE.search(value):
        raise ValidationError(f"{label} contains path traversal sequence")

    if _QUERY_FRAGMENT_RE.search(value):
        raise ValidationError(
            f"{label} contains invalid characters (? or #) — pass the resource ID only, not a URL"
        )

    if _PERCENT_ENCODED_RE.search(value):
        raise ValidationError(
            f"{label} contains percent-encoded characters — pass raw values, not URL-encoded"
        )

    return value


def validate_free_text(value: str, label: str) -> str:
    """Validate natural-language input (questions, search terms, comments).

    Only rejects control characters — questions contain '?', and that's fine.

    Raises:
        ValidationError: If control characters are found.
    """
    if _CONTROL_RE.search(value):
        raise ValidationError(f"{label} contains control characters")

    return value
