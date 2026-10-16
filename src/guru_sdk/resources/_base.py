"""Base resource class — shared infrastructure for all resource modules.

Provides the HttpClient reference and common patterns like resolve-by-name.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# Page cap for listings whose miss raises NotFoundError (name resolution, home
# folder lookup). A plain list() can stop at the default 10 pages and report
# truncation via PaginatedList.complete; a lookup that concludes "not found"
# must not, or it rejects names that exist past the cap.
RESOLVE_MAX_PAGES = 100


class BaseResource:
    """Base class for all Guru API resource modules."""

    def __init__(self, http: HttpClient) -> None:
        self._http = http
