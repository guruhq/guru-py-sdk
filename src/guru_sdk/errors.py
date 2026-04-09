"""Typed exception hierarchy for guru-sdk.

Mirrors the guru-cli pattern: a base error, HTTP-status-specific subclasses,
and a client-side validation error. Callers use try/except with the specific
subclass they care about — everything else bubbles up as GuruError.
"""

from __future__ import annotations

from typing import Any

# =============================================================================
# Base Errors
# =============================================================================


class GuruError(Exception):
    """Base for all guru-sdk errors."""


class GuruApiError(GuruError):
    """An error response from the Guru API.

    Attributes:
        status_code: HTTP status code from the response.
        message: Parsed error message from the response body.
        body: Raw response body (JSON dict or string).
    """

    def __init__(self, status_code: int, body: Any = None) -> None:
        self.status_code = status_code
        self.body = body
        self.message = self._parse_message(body)
        super().__init__(f"[{status_code}] {self.message}")

    @staticmethod
    def _parse_message(body: Any) -> str:
        """Extract a human-readable message from the response body."""
        if isinstance(body, dict):
            # Guru API error responses typically have a "message" field
            for key in ("message", "error", "detail"):
                val = body.get(key)
                if isinstance(val, str):
                    return val
            return str(body)
        if isinstance(body, str) and body:
            return body
        return "Unknown error"


# =============================================================================
# HTTP Status-Specific Errors
# =============================================================================


class AuthenticationError(GuruApiError):
    """401 Unauthorized — invalid or missing credentials."""

    def __init__(self, body: Any = None) -> None:
        super().__init__(401, body or "Invalid or missing credentials. Check GURU_USER and GURU_TOKEN.")


class ForbiddenError(GuruApiError):
    """403 Forbidden — valid credentials but insufficient permissions."""

    def __init__(self, body: Any = None) -> None:
        super().__init__(403, body or "Insufficient permissions for this operation.")


class NotFoundError(GuruApiError):
    """404 Not Found — the requested resource does not exist."""

    def __init__(self, body: Any = None) -> None:
        super().__init__(404, body or "Resource not found.")


class RateLimitError(GuruApiError):
    """429 Too Many Requests — rate limit exceeded."""

    def __init__(self, body: Any = None) -> None:
        super().__init__(429, body or "Rate limit exceeded. Retry after a delay.")


# =============================================================================
# Client-Side Errors
# =============================================================================


class ValidationError(GuruError):
    """Client-side input validation failure.

    Raised before any HTTP request is made — the input is malformed.
    Mirrors guru-cli's InputValidationError.
    """
