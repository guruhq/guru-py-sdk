"""Guru SDK client — the public entry point.

Composes all resource modules into a single facade. Mirrors the guru-cli
GuruClient pattern: one property per resource group, all wired to a shared
HttpClient instance.

Usage::

    from guru_sdk import Guru

    g = Guru()  # reads GURU_USER + GURU_TOKEN from env
    card = g.cards.get("card-id")
    folders = g.folders.list()

Credentials are resolved in order:
1. Explicit arguments (username, api_token)
2. GURU_USER / GURU_TOKEN environment variables
3. PYGURU_USER / PYGURU_TOKEN (backward compat with py-sdk v1)
"""

from __future__ import annotations

import os

from guru_sdk.errors import AuthenticationError
from guru_sdk.http import DEFAULT_BASE_URL, QA_BASE_URL, HttpClient
from guru_sdk.resources.agents import AgentResource
from guru_sdk.resources.announcements import AnnouncementResource
from guru_sdk.resources.answers import AnswerResource
from guru_sdk.resources.cards import CardResource
from guru_sdk.resources.collections import CollectionResource
from guru_sdk.resources.drafts import DraftResource
from guru_sdk.resources.folders import FolderResource
from guru_sdk.resources.groups import GroupResource
from guru_sdk.resources.members import MemberResource
from guru_sdk.resources.page_drafts import PageDraftResource
from guru_sdk.resources.pages import PageResource
from guru_sdk.resources.search import SearchResource
from guru_sdk.resources.sources import SourceResource
from guru_sdk.resources.tags import TagResource

# =============================================================================
# Public API
# =============================================================================


class Guru:
    """Guru SDK client.

    Args:
        username: Guru account email. Falls back to GURU_USER / PYGURU_USER env vars.
        api_token: Guru API token. Falls back to GURU_TOKEN / PYGURU_TOKEN env vars.
        base_url: API base URL. Override for testing or on-prem deployments.
            Also reads GURU_BASE_URL env var as fallback.
        qa: **Internal only.** If True, target the Guru QA environment
            (qaapi.getguru.com). Requires Guru-internal QA credentials.
            Cannot be combined with an explicit base_url.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(
        self,
        username: str | None = None,
        api_token: str | None = None,
        *,
        base_url: str | None = None,
        qa: bool = False,
        timeout: float = 30.0,
    ) -> None:
        # Validate that qa and explicit base_url are not both specified
        if qa and base_url is not None:
            msg = (
                "Cannot specify both qa=True and base_url. "
                "Use qa=True for the QA environment, or base_url for a custom URL."
            )
            raise ValueError(msg)

        # Resolve base URL: explicit arg → qa flag → GURU_BASE_URL env var → default
        if base_url is not None:
            resolved_url = base_url
        elif qa:
            resolved_url = QA_BASE_URL
        else:
            resolved_url = os.environ.get("GURU_BASE_URL") or DEFAULT_BASE_URL

        # Resolve credentials from arguments → env vars (with py-sdk v1 fallback)
        resolved_user = username or os.environ.get("GURU_USER") or os.environ.get("PYGURU_USER")
        resolved_token = api_token or os.environ.get("GURU_TOKEN") or os.environ.get("PYGURU_TOKEN")

        if not resolved_user or not resolved_token:
            raise AuthenticationError(
                "Missing credentials. Provide username/api_token arguments or set "
                "GURU_USER and GURU_TOKEN environment variables."
            )

        self._http = HttpClient(
            base_url=resolved_url,
            username=resolved_user,
            api_token=resolved_token,
            timeout=timeout,
        )

        # Resource modules — one property per resource group, all sharing the
        # same HttpClient. Mirrors guru-cli's facade pattern.
        self.agents = AgentResource(self._http)
        self.announcements = AnnouncementResource(self._http)
        self.answers = AnswerResource(self._http)
        self.cards = CardResource(self._http)
        self.collections = CollectionResource(self._http)
        self.drafts = DraftResource(self._http)
        self.folders = FolderResource(self._http)
        self.groups = GroupResource(self._http)
        self.members = MemberResource(self._http)
        self.page_drafts = PageDraftResource(self._http)
        self.pages = PageResource(self._http)
        self.search = SearchResource(self._http)
        self.sources = SourceResource(self._http)
        self.tags = TagResource(self._http)

    # -------------------------------------------------------------------------
    # Context manager support — clean up httpx client
    # -------------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP client and release connections."""
        self._http.close()

    def __enter__(self) -> Guru:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
