"""Tests for guru_sdk.resources.drafts — DraftResource.

TDD tests covering the draft API surface (CRD + collaborators — no update):
- list() — list all drafts or filter by card ID (GET /drafts)
- get() — get a specific draft (GET /drafts/{draftId})
- create() — create a new draft (POST /drafts)
- delete() — delete a draft (DELETE /drafts/{draftId})
- list_collaborators() — list collaborators (GET /drafts/{id}/collaborators)
- add_collaborators() — add collaborators (POST /drafts/{id}/collaborators)
- remove_collaborator() — remove collaborator (DELETE /drafts/{id}/collaborators/{cId})
- Input validation

Update is explicitly deferred due to collaborative editing (MPS/YJS) complexity.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import DraftCard
from guru_sdk.models._manual import DraftCollaborator
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
COLLAB_UUID = "e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5"
GROUP_UUID = "f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6"


def _collaborator_json(
    collab_id: str = COLLAB_UUID,
    email: str = "collab@example.com",
) -> dict:
    """Build a realistic DraftCollaborator API response dict."""
    return {
        "id": collab_id,
        "type": "user",
        "user": {
            "email": email,
            "firstName": "Collab",
            "lastName": "User",
        },
        "dateCreated": "2025-06-15T10:00:00.000+0000",
    }


def _group_collaborator_json(
    collab_id: str = GROUP_UUID,
    group_id: str = GROUP_UUID,
) -> dict:
    """Build a realistic group DraftCollaborator API response dict."""
    return {
        "id": collab_id,
        "type": "user-group",
        "userGroup": {"id": group_id},
        "dateCreated": "2025-06-15T10:00:00.000+0000",
    }


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

    def test_list_all(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_list_empty(self, drafts: DraftResource, httpx_mock) -> None:
        """No drafts returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=[],
        )
        result = drafts.list()
        assert result == []

    def test_list_by_card_id(self, drafts: DraftResource, httpx_mock) -> None:
        """Filtering by card_id passes query param."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts?cardId={CARD_UUID}",
            json=[_draft_json(DRAFT_UUID, "Card Draft", card_id=CARD_UUID)],
        )
        result = drafts.list(card_id=CARD_UUID)
        assert len(result) == 1
        assert result[0].card_id == CARD_UUID

    def test_draft_nested_fields(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_get_by_id(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_create_minimal(self, drafts: DraftResource, httpx_mock) -> None:
        """Create a draft with just a title."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/drafts",
            json=_draft_json(),
            status_code=201,
        )
        result = drafts.create(title="Draft Card")
        assert isinstance(result, DraftCard)
        assert result.title == "Draft Card"

    def test_create_sends_body(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_create_with_all_fields(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_create_omits_none_fields(self, drafts: DraftResource, httpx_mock) -> None:
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

    def test_delete(self, drafts: DraftResource, httpx_mock) -> None:
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


# =============================================================================
# list_collaborators() — GET /drafts/{draftId}/collaborators
# =============================================================================


class TestListCollaborators:
    """List collaborators on a draft."""

    def test_list_collaborators(self, drafts: DraftResource, httpx_mock) -> None:
        """List returns DraftCollaborator objects."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json(), _collaborator_json("c2", "other@example.com")],
        )
        result = drafts.list_collaborators(DRAFT_UUID)
        assert len(result) == 2
        assert isinstance(result[0], DraftCollaborator)
        assert result[0].type == "user"
        assert result[0].user is not None
        assert result[0].user.email == "collab@example.com"
        assert result[1].user is not None
        assert result[1].user.email == "other@example.com"

    def test_list_collaborators_empty(self, drafts: DraftResource, httpx_mock) -> None:
        """No collaborators returns empty list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[],
        )
        result = drafts.list_collaborators(DRAFT_UUID)
        assert result == []

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.list_collaborators("")


# =============================================================================
# add_collaborators() — POST /drafts/{draftId}/collaborators
# =============================================================================


class TestAddCollaborators:
    """Add collaborators to a draft."""

    def test_add_collaborators(self, drafts: DraftResource, httpx_mock) -> None:
        """Add collaborators returns the updated list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json()],
        )
        collabs = [{"type": "user", "user": {"email": "collab@example.com"}}]
        result = drafts.add_collaborators(DRAFT_UUID, collabs)
        assert len(result) == 1
        assert isinstance(result[0], DraftCollaborator)
        assert result[0].user is not None
        assert result[0].user.email == "collab@example.com"

    def test_add_collaborators_body(self, drafts: DraftResource, httpx_mock) -> None:
        """Verify the request body wraps collaborators."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json()],
        )
        collabs = [{"type": "user", "user": {"email": "collab@example.com"}}]
        drafts.add_collaborators(DRAFT_UUID, collabs)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "collaborators" in body
        assert body["collaborators"] == collabs

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.add_collaborators("", [])


# =============================================================================
# remove_collaborator() — DELETE /drafts/{draftId}/collaborators/{collaboratorId}
# =============================================================================


class TestRemoveCollaborator:
    """Remove a collaborator from a draft."""

    def test_remove_collaborator(self, drafts: DraftResource, httpx_mock) -> None:
        """Delete removes a collaborator."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators/{COLLAB_UUID}",
            method="DELETE",
            status_code=204,
        )
        # Should not raise
        drafts.remove_collaborator(DRAFT_UUID, COLLAB_UUID)

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.remove_collaborator("", COLLAB_UUID)

    def test_validates_collaborator_id(self, drafts: DraftResource) -> None:
        """Empty collaborator_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.remove_collaborator(DRAFT_UUID, "")


# =============================================================================
# add_group_collaborators() — POST /drafts/{draftId}/collaborators (group type)
# =============================================================================


class TestAddGroupCollaborators:
    """Add group collaborators to a draft."""

    def test_add_group_collaborators_body(self, drafts: DraftResource, httpx_mock) -> None:
        """POST body is correctly shaped for group collaborators."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_group_collaborator_json()],
        )
        drafts.add_group_collaborators(DRAFT_UUID, [GROUP_UUID])
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"collaborators": [{"type": "user-group", "userGroup": {"id": GROUP_UUID}}]}

    def test_add_group_collaborators_returns_collaborators(
        self, drafts: DraftResource, httpx_mock
    ) -> None:
        """Returns a list of DraftCollaborator objects."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_group_collaborator_json()],
        )
        result = drafts.add_group_collaborators(DRAFT_UUID, [GROUP_UUID])
        assert len(result) == 1
        assert isinstance(result[0], DraftCollaborator)
        assert result[0].type == "user-group"

    def test_user_group_field_populated(self, drafts: DraftResource, httpx_mock) -> None:
        """Response with userGroup key populates .user_group on DraftCollaborator."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators",
            json=[_group_collaborator_json(group_id=GROUP_UUID)],
        )
        result = drafts.add_group_collaborators(DRAFT_UUID, [GROUP_UUID])
        collab = result[0]
        assert collab.type == "user-group"
        assert collab.user_group is not None
        assert collab.user_group["id"] == GROUP_UUID

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.add_group_collaborators("", [GROUP_UUID])

    def test_validates_group_id(self, drafts: DraftResource) -> None:
        """Empty string in group_ids list raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.add_group_collaborators(DRAFT_UUID, [""])


# =============================================================================
# remove_group_collaborator() — DELETE /drafts/{draftId}/collaborators/{groupId}
# =============================================================================


class TestRemoveGroupCollaborator:
    """Remove a group collaborator from a draft."""

    def test_remove_group_collaborator(self, drafts: DraftResource, httpx_mock) -> None:
        """Delete removes a group collaborator by group UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/drafts/{DRAFT_UUID}/collaborators/{GROUP_UUID}",
            method="DELETE",
            status_code=204,
        )
        # Should not raise
        drafts.remove_group_collaborator(DRAFT_UUID, GROUP_UUID)

    def test_validates_draft_id(self, drafts: DraftResource) -> None:
        """Empty draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.remove_group_collaborator("", GROUP_UUID)

    def test_validates_group_id(self, drafts: DraftResource) -> None:
        """Empty group_id raises ValidationError."""
        with pytest.raises(ValidationError):
            drafts.remove_group_collaborator(DRAFT_UUID, "")
