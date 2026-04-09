"""Synchronous HTTP transport for the Guru API.

The only file that touches httpx. Every request goes through here — auth,
headers, serialization, error mapping, pagination. Resource classes never
see raw HTTP; they call http.get(), http.post(), etc. and receive validated
Pydantic models back.

Architecture note: uses httpx.Client (sync). When async demand materializes,
an AsyncHttpClient with httpx.AsyncClient can be added alongside this one
with the same interface — no changes to existing code.
"""

from __future__ import annotations

import re
from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter

from guru_sdk._version import __version__
from guru_sdk.errors import (
    AuthenticationError,
    ForbiddenError,
    GuruApiError,
    NotFoundError,
    RateLimitError,
)
from guru_sdk.models._base import GuruModel

# =============================================================================
# Constants
# =============================================================================

DEFAULT_BASE_URL = "https://api.getguru.com/api/v1"

# Tracking headers so Guru can identify SDK traffic
_TRACKING_HEADERS = {
    "User-Agent": f"guru-sdk-python/{__version__}",
    "X-Guru-SDK": f"python/{__version__}",
}

_T = TypeVar("_T", bound=GuruModel)

# =============================================================================
# Public API — HttpClient
# =============================================================================


class HttpClient:
    """Synchronous HTTP transport for the Guru API.

    All methods validate responses against Pydantic models and raise typed
    exceptions on HTTP errors.
    """

    def __init__(
        self,
        base_url: str,
        username: str,
        api_token: str,
        *,
        timeout: float = 30.0,
        _client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        # Allow injecting a pre-built httpx.Client for testing (pytest-httpx).
        # In production, we build our own with auth and tracking headers.
        self._client = _client or httpx.Client(
            base_url=self._base_url,
            auth=(username, api_token),
            headers={
                **_TRACKING_HEADERS,
                "Accept": "application/json",
            },
            timeout=timeout,
            proxy=None,
        )

    # -------------------------------------------------------------------------
    # Request methods — typed responses via Pydantic model validation
    # -------------------------------------------------------------------------

    def get(self, path: str, model: type[_T], **params: Any) -> _T:
        """GET a single resource and validate against *model*."""
        response = self._client.get(path, params=params or None)
        self._raise_for_status(response)
        return model.model_validate(response.json())

    def get_list(self, path: str, model: type[_T], **params: Any) -> list[_T]:
        """GET a list endpoint and validate each item against *model*."""
        response = self._client.get(path, params=params or None)
        self._raise_for_status(response)
        # Some endpoints return 204 No Content for empty lists
        if response.status_code == 204:
            return []
        adapter = TypeAdapter(list[model])  # type: ignore[valid-type]
        return adapter.validate_python(response.json())

    def post(self, path: str, body: Any, model: type[_T]) -> _T:
        """POST with JSON body and validate the response against *model*."""
        response = self._client.post(path, json=body)
        self._raise_for_status(response)
        return model.model_validate(response.json())

    def post_no_content(self, path: str, body: Any = None) -> None:
        """POST that expects no response body (e.g., adding a tag to a card)."""
        response = self._client.post(path, json=body)
        self._raise_for_status(response)

    def put(self, path: str, body: Any, model: type[_T]) -> _T:
        """PUT with JSON body and validate the response against *model*."""
        response = self._client.put(path, json=body)
        self._raise_for_status(response)
        return model.model_validate(response.json())

    def delete(self, path: str) -> None:
        """DELETE a resource. Expects no response body."""
        response = self._client.delete(path)
        self._raise_for_status(response)

    # -------------------------------------------------------------------------
    # Pagination — follows Link headers to aggregate all pages
    # -------------------------------------------------------------------------

    def get_paginated(
        self,
        path: str,
        model: type[_T],
        *,
        max_pages: int = 10,
    ) -> list[_T]:
        """GET all pages of a paginated endpoint.

        Follows Link: <url>; rel="next" headers up to *max_pages*.
        """
        all_items: list[_T] = []
        # First request uses the relative path through the httpx client
        next_url: str | None = path
        page = 0
        adapter = TypeAdapter(list[model])  # type: ignore[valid-type]

        while next_url is not None and page < max_pages:
            response = self._client.get(next_url)

            self._raise_for_status(response)

            if response.status_code == 204:
                break

            items = adapter.validate_python(response.json())
            all_items.extend(items)
            page += 1

            # Parse Link header for next page
            next_url = _parse_link_header(response.headers.get("link"))

        return all_items

    # -------------------------------------------------------------------------
    # Cleanup
    # -------------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying httpx client."""
        self._client.close()

    def __enter__(self) -> HttpClient:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    # -------------------------------------------------------------------------
    # Private — error mapping
    # -------------------------------------------------------------------------

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Convert HTTP error responses to typed exceptions."""
        if response.is_success:
            return

        # Try to parse JSON body for error details
        try:
            body: Any = response.json()
        except Exception:
            body = response.text

        match response.status_code:
            case 401:
                raise AuthenticationError(body)
            case 403:
                raise ForbiddenError(body)
            case 404:
                raise NotFoundError(body)
            case 429:
                raise RateLimitError(body)
            case _:
                raise GuruApiError(response.status_code, body)


# =============================================================================
# Internal Helpers
# =============================================================================

# Link: <https://api.getguru.com/api/v1/folders?page=2>; rel="next"
_LINK_NEXT_RE = re.compile(r'<([^>]+)>;\s*rel="next"')


def _parse_link_header(header: str | None) -> str | None:
    """Extract the 'next' URL from a Link header. Returns None if absent."""
    if not header:
        return None
    match = _LINK_NEXT_RE.search(header)
    return match.group(1) if match else None
