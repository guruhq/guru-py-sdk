"""Base resource class — shared infrastructure for all resource modules.

Provides the HttpClient reference and common patterns like resolve-by-name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient


class BaseResource:
    """Base class for all Guru API resource modules."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
