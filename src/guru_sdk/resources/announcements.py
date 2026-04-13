"""Announcement resource — broadcast cards to groups.

Announcements (internally "alerts") let you push a card to one or more groups,
then track read stats. The API uses "alerts" for the endpoint name; the SDK
uses "announcements" to match Guru product terminology.

API surface mirrors guru-cli's AnnouncementResource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import (
    AnnouncementInsightSummary,
    KnowledgeAlertDelegated,
)
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — AnnouncementResource
# =============================================================================


class AnnouncementResource(BaseResource):
    """Guru Announcements — broadcast cards and track stats.

    Methods:
        list()   — list all announcements (GET /alerts)
        create() — broadcast a card to groups (POST /alerts)
        stats()  — get read stats (GET /announcements/{id}/stats/summary)
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self) -> builtins.list[KnowledgeAlertDelegated]:
        """List all announcements."""
        return self._http.get_list("/alerts", KnowledgeAlertDelegated)

    def stats(self, announcement_id: str) -> AnnouncementInsightSummary:
        """Get read stats for an announcement.

        Args:
            announcement_id: Announcement UUID.
        """
        validate_input(announcement_id, "announcement_id")
        return self._http.get(
            f"/announcements/{announcement_id}/stats/summary",
            AnnouncementInsightSummary,
        )

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def create(
        self,
        *,
        card_id: str,
        group_ids: builtins.list[str],
        note: str | None = None,
    ) -> KnowledgeAlertDelegated:
        """Create an announcement — broadcast a card to one or more groups.

        Args:
            card_id: ID of the card to broadcast.
            group_ids: List of group UUIDs to send the announcement to.
            note: Optional note included with the announcement.
        """
        validate_input(card_id, "card_id")
        if not group_ids:
            raise ValidationError("group_ids must not be empty")
        for gid in group_ids:
            validate_input(gid, "group_id")
        if note is not None:
            validate_free_text(note, "note")

        body: dict[str, Any] = {
            "cardId": card_id,
            "groups": [{"id": gid} for gid in group_ids],
        }
        if note is not None:
            body["note"] = note
        return self._http.post("/alerts", body, KnowledgeAlertDelegated)
