"""Tests for guru_sdk.resources.announcements — AnnouncementResource.

TDD tests covering the announcement API surface:
- list() — list all announcements (GET /alerts)
- create() — broadcast a card (POST /alerts)
- stats() — get read stats (GET /announcements/{id}/stats/summary)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import (
    AnnouncementInsightSummary,
    KnowledgeAlertDelegated,
)
from guru_sdk.resources.announcements import AnnouncementResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

ANNOUNCE_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
CARD_UUID = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
GROUP_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
GROUP_UUID_2 = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"


def _announcement_json(
    alert_id: str = ANNOUNCE_UUID,
    card_title: str = "Important Update",
) -> dict:
    """Build a realistic KnowledgeAlertDelegated API response dict."""
    return {
        "alertId": alert_id,
        "card": {
            "id": CARD_UUID,
            "preferredPhrase": card_title,
            "content": "<p>Card content</p>",
        },
        "cardTitle": card_title,
        "note": "Please read this update.",
        "dateSent": "2025-06-15T10:00:00.000+0000",
        "percentRead": 75,
        "readCount": 30,
        "unreadCount": 10,
        "collectionHexColor": "#4A90D9",
        "sentBy": {
            "email": "admin@example.com",
            "firstName": "Admin",
            "lastName": "User",
        },
        "groups": [
            {
                "id": GROUP_UUID,
                "name": "Engineering",
                "dateCreated": "2025-01-01T00:00:00.000+0000",
            }
        ],
    }


def _stats_json() -> dict:
    """Build a realistic AnnouncementInsightSummary API response dict."""
    return {
        "readCount": 30,
        "unreadCount": 10,
        "openedCount": 35,
        "unopenedCount": 5,
        "currentUserReadDate": "2025-06-15T12:00:00.000+0000",
        "currentUserAnnouncementUser": True,
        "announcement": {
            "id": ANNOUNCE_UUID,
            "dateCreated": "2025-06-15T10:00:00.000+0000",
            "cardId": CARD_UUID,
            "note": "Please read this update.",
        },
        "readUsers": [
            {
                "email": "reader@example.com",
                "firstName": "Reader",
                "lastName": "One",
                "announcementReadAt": "2025-06-15T11:00:00.000+0000",
                "announcementViewedAt": "2025-06-15T10:30:00.000+0000",
            }
        ],
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def announcements(http_client: HttpClient) -> AnnouncementResource:
    """AnnouncementResource wired to the mock HttpClient."""
    return AnnouncementResource(http_client)


# =============================================================================
# list() — GET /alerts
# =============================================================================


class TestList:
    """List all announcements."""

    def test_list_all(self, announcements: AnnouncementResource, httpx_mock) -> None:
        """List announcements returns list of KnowledgeAlertDelegated objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=[
                _announcement_json(ANNOUNCE_UUID, "First Update"),
                _announcement_json("a2a2a2a2-a2a2-a2a2-a2a2-a2a2a2a2a2a2", "Second Update"),
            ],
        )
        result = announcements.list()
        assert len(result) == 2
        assert isinstance(result[0], KnowledgeAlertDelegated)
        assert result[0].card_title == "First Update"

    def test_list_empty(self, announcements: AnnouncementResource, httpx_mock) -> None:
        """No announcements returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=[],
        )
        result = announcements.list()
        assert result == []

    def test_announcement_nested_fields(
        self, announcements: AnnouncementResource, httpx_mock
    ) -> None:
        """KnowledgeAlertDelegated parses nested sentBy and groups."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=[_announcement_json()],
        )
        result = announcements.list()
        ann = result[0]
        assert ann.sent_by is not None
        assert ann.sent_by.email == "admin@example.com"
        assert ann.groups is not None
        assert len(ann.groups) == 1
        assert ann.groups[0].name == "Engineering"


# =============================================================================
# create() — POST /alerts
# =============================================================================


class TestCreate:
    """Create an announcement — broadcast a card."""

    def test_create(self, announcements: AnnouncementResource, httpx_mock) -> None:
        """Create returns KnowledgeAlertDelegated."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=_announcement_json(),
        )
        result = announcements.create(card_id=CARD_UUID, group_ids=[GROUP_UUID])
        assert isinstance(result, KnowledgeAlertDelegated)
        assert result.card_title == "Important Update"

    def test_create_sends_body(self, announcements: AnnouncementResource, httpx_mock) -> None:
        """Create sends cardId, groups array, and optional note."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=_announcement_json(),
        )
        announcements.create(
            card_id=CARD_UUID,
            group_ids=[GROUP_UUID, GROUP_UUID_2],
            note="Important!",
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["cardId"] == CARD_UUID
        assert body["groups"] == [{"id": GROUP_UUID}, {"id": GROUP_UUID_2}]
        assert body["note"] == "Important!"

    def test_create_omits_note_when_none(
        self, announcements: AnnouncementResource, httpx_mock
    ) -> None:
        """Note field is omitted when not provided."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/alerts",
            json=_announcement_json(),
        )
        announcements.create(card_id=CARD_UUID, group_ids=[GROUP_UUID])
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "note" not in body

    def test_create_validates_card_id(self, announcements: AnnouncementResource) -> None:
        """Empty card_id raises ValidationError."""
        with pytest.raises(ValidationError):
            announcements.create(card_id="", group_ids=[GROUP_UUID])

    def test_create_validates_group_ids(self, announcements: AnnouncementResource) -> None:
        """Empty group_id in list raises ValidationError."""
        with pytest.raises(ValidationError):
            announcements.create(card_id=CARD_UUID, group_ids=[""])

    def test_create_validates_empty_group_list(
        self, announcements: AnnouncementResource
    ) -> None:
        """Empty group_ids list raises ValidationError."""
        with pytest.raises(ValidationError):
            announcements.create(card_id=CARD_UUID, group_ids=[])


# =============================================================================
# stats() — GET /announcements/{id}/stats/summary
# =============================================================================


class TestStats:
    """Get read stats for an announcement."""

    def test_stats(self, announcements: AnnouncementResource, httpx_mock) -> None:
        """Stats returns AnnouncementInsightSummary."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/announcements/{ANNOUNCE_UUID}/stats/summary",
            json=_stats_json(),
        )
        result = announcements.stats(ANNOUNCE_UUID)
        assert isinstance(result, AnnouncementInsightSummary)
        assert result.read_count == 30
        assert result.unread_count == 10
        assert result.read_users is not None
        assert len(result.read_users) == 1

    def test_validates_announcement_id(self, announcements: AnnouncementResource) -> None:
        """Empty announcement_id raises ValidationError."""
        with pytest.raises(ValidationError):
            announcements.stats("")
