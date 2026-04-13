"""Tests for guru_sdk.resources.drafts — DraftResource.

TDD tests covering the draft API surface (CRD only — no update):
- list() — list all drafts or filter by card ID (GET /drafts)
- get() — get a specific draft (GET /drafts/{draftId})
- create() — create a new draft (POST /drafts)
- delete() — delete a draft (DELETE /drafts/{draftId})
- Input validation

Update is explicitly deferred due to collaborative editing (MPS/YJS) complexity.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import DraftCard
from guru_sdk.resources.drafts import DraftResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

DRAFT_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
DRAFT_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
CARD_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
COLLECTION_UUID = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"


def _draft_json(
    draft_id: str = DRAFT_UUID,
    title: str = "Draft Card",
    card_id: str | None = None,
) -> dict:
    """Build a realistic DraftCard API response dict."""
    result: dict = {
        "id": draft_id,
        "title": title,
        "content": "<p>Draft content here</p>",
        "lastModified": "2025-06-15T10:00:00.000+0000",
        "version": 1,
        "user": {
            "email": "author@example.com",
            "firstName": "Draft",
            "lastName": "Author",
        },
        "collection": {
            "id": COLLECTION_UUID,
            "name": "Engineering",
            "color": "#4A90D9",
        },
    }
    if card_id is not None:
        result["cardId"] = card_id
    return result


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def drafts(http_client: HttpClient) -> DraftResource:
    """DraftResource wired to the mock HttpClient."""
    return DraftResource(http_client)


# =============================================================================
# list() — GET /drafts
# =============================================================================


class TestList:
    """List drafts, optionally filtered by card ID."""

    def test_list_all(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """List all drafts returns list of DraftCard objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=[
                _draft_json(DRAFT_UUID, "First Draft"),
                _draft_json(DRAFT_UUID_2, "Second Draft"),
            ],
        )
        result = drafts.list()
        assert len(result) == 2
        assert isinstance(result[0], DraftCard)
        assert result[0].title == "First Draft"
        assert result[1].title == "Second Draft"

    def test_list_empty(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """No drafts returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=[],
        )
        result = drafts.list()
        assert result == []

    def test_list_by_card_id(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Filtering by card_id passes query param."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts?cardId={CARD_UUID}",
            json=[_draft_json(DRAFT_UUID, "Card Draft", card_id=CARD_UUID)],
        )
        result = drafts.list(card_id=CARD_UUID)
        assert len(result) == 1
        assert result[0].card_id == CARD_UUID

    def test_draft_nested_fields(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """DraftCard model correctly parses nested user and collection."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=[_draft_json()],
        )
        result = drafts.list()
        draft = result[0]
        assert draft.user is not None
        assert draft.user.email == "author@example.com"
        assert draft.collection is not None
        assert draft.collection.name == "Engineering"


# =============================================================================
# get() — GET /drafts/{draftId}
# =============================================================================


class TestGet:
    """Get a specific draft by ID."""

    def test_get_by_id(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Get a draft by UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}",
            json=_draft_json(),
        )
        result = drafts.get(DRAFT_UUID)
        assert isinstance(result, DraftCard)
        assert result.id == DRAFT_UUID
        assert result.title == "Draft Card"

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.get("")

    def test_validates_control_chars(self, drafts: DraftResource) -> None:
        """Control chars in draft_id are rejected."""
        with pytest.raises(ValidationError):
            drafts.get("draft\x00id")


# =============================================================================
# create() — POST /drafts
# =============================================================================


class TestCreate:
    """Create a new draft card."""

    def test_create_minimal(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Create a draft with just a title."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=_draft_json(),
            status_code=201,
        )
        result = drafts.create(title="Draft Card")
        assert isinstance(result, DraftCard)
        assert result.title == "Draft Card"

    def test_create_sends_body(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Create sends title and content in the POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=_draft_json(),
            status_code=201,
        )
        drafts.create(title="My Draft", content="<p>Hello</p>")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["title"] == "My Draft"
        assert body["content"] == "<p>Hello</p>"

    def test_create_with_all_fields(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Create with all optional fields."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=_draft_json(card_id=CARD_UUID),
            status_code=201,
        )
        drafts.create(
            title="Updated Draft",
            content="<p>New content</p>",
            json_content='{"type":"doc"}',
            card_id=CARD_UUID,
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["title"] == "Updated Draft"
        assert body["content"] == "<p>New content</p>"
        assert body["jsonContent"] == '{"type":"doc"}'
        assert body["cardId"] == CARD_UUID

    def test_create_omits_none_fields(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """None/default fields are not sent in the body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=_draft_json(),
            status_code=201,
        )
        drafts.create(title="Simple Draft")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"title": "Simple Draft"}

    def test_create_validates_title(self, drafts: DraftResource) -> None:
        """Empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.create(title="")


# =============================================================================
# delete() — DELETE /drafts/{draftId}
# =============================================================================


class TestDelete:
    """Delete a draft."""

    def test_delete(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Delete a draft by ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}",
            method="DELETE",
            status_code=204,
        )
        # Should not raise
        drafts.delete(DRAFT_UUID)

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.delete("")
