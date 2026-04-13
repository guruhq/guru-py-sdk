"""Tests for guru_sdk.resources.page_drafts — PageDraftResource.

TDD tests covering the page draft API surface (CRD + collaborators — no update):
- list() — list all page drafts or filter by page ID (GET /pagedrafts)
- get() — get a page draft by ID (GET /pagedrafts/{pageDraftId})
- create() — create a page draft (POST /pagedrafts)
- delete() — delete a page draft (DELETE /pagedrafts/{pageDraftId})
- list_collaborators() — list collaborators (GET /pagedrafts/{id}/collaborators)
- add_collaborators() — add collaborators (POST /pagedrafts/{id}/collaborators)
- update_collaborators() — update collaborator roles (PUT /pagedrafts/{id}/collaborators)
- remove_collaborator() — remove collaborator (DELETE /pagedrafts/{id}/collaborators/{cId})
- Input validation

Update is deferred due to MPS/YJS collaborative editing — same constraint as card drafts.
All endpoints are internal API (not in public Swagger) — mirrors guru-cli ADR-014.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._manual import PageDraft, PageDraftCollaborator
from guru_sdk.resources.page_drafts import PageDraftResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

DRAFT_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
DRAFT_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
PAGE_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
AGENT_UUID = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"
PARENT_UUID = "e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5"
COLLAB_UUID = "f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6"


def _page_draft_json(
    draft_id: str = DRAFT_UUID,
    title: str = "Draft Page",
    *,
    page_id: str | None = None,
) -> dict:
    """Build a realistic PageDraft API response dict."""
    result: dict = {
        "id": draft_id,
        "title": title,
        "jsonContent": '{"type":"doc","content":[]}',
        "heroImage": "https://example.com/hero.png",
        "badgeEmoji": ":rocket:",
        "draft": True,
        "editable": True,
        "onlyNavigable": False,
        "dateCreated": "2025-06-01T10:00:00.000+0000",
        "lastModified": "2025-06-15T14:30:00.000+0000",
        "lastModifiedBy": {
            "email": "editor@example.com",
            "firstName": "Page",
            "lastName": "Editor",
        },
        "createdBy": {
            "email": "creator@example.com",
            "firstName": "Page",
            "lastName": "Creator",
        },
        "team": {
            "id": "t1t1t1t1-t1t1-t1t1-t1t1-t1t1t1t1t1t1",
            "dateCreated": "2025-01-01T00:00:00.000+0000",
        },
    }
    if page_id is not None:
        result["pageId"] = page_id
    return result


def _collaborator_json(
    collab_id: str = COLLAB_UUID,
    collab_type: str = "user",
) -> dict:
    """Build a page draft collaborator response dict."""
    result: dict = {
        "id": collab_id,
        "type": collab_type,
        "objectRole": {"id": "role-1", "name": "Editor"},
    }
    if collab_type == "user":
        result["user"] = {
            "email": "collab@example.com",
            "firstName": "Collab",
            "lastName": "User",
        }
    return result


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def page_drafts(http_client: HttpClient) -> PageDraftResource:
    """PageDraftResource wired to the mock HttpClient."""
    return PageDraftResource(http_client)


# =============================================================================
# list() — GET /pagedrafts
# =============================================================================


class TestList:
    """List page drafts, optionally filtered by page ID."""

    def test_list_all(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """List all page drafts returns list of PageDraft objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=[
                _page_draft_json(DRAFT_UUID, "First Draft"),
                _page_draft_json(DRAFT_UUID_2, "Second Draft"),
            ],
        )
        result = page_drafts.list()
        assert len(result) == 2
        assert isinstance(result[0], PageDraft)
        assert result[0].title == "First Draft"
        assert result[1].title == "Second Draft"

    def test_list_empty(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """No page drafts returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=[],
        )
        result = page_drafts.list()
        assert result == []

    def test_list_by_page_id(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Filtering by page_id passes query param."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts?pageId={PAGE_UUID}",
            json=[_page_draft_json(DRAFT_UUID, "Page Draft", page_id=PAGE_UUID)],
        )
        result = page_drafts.list(page_id=PAGE_UUID)
        assert len(result) == 1
        assert result[0].page_id == PAGE_UUID

    def test_draft_nested_fields(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """PageDraft model correctly parses nested user and team."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=[_page_draft_json()],
        )
        result = page_drafts.list()
        draft = result[0]
        assert draft.last_modified_by is not None
        assert draft.last_modified_by.email == "editor@example.com"
        assert draft.created_by is not None
        assert draft.created_by.email == "creator@example.com"
        assert draft.team is not None


# =============================================================================
# get() — GET /pagedrafts/{pageDraftId}
# =============================================================================


class TestGet:
    """Get a page draft by ID."""

    def test_get_by_id(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Get a page draft by UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}",
            json=_page_draft_json(),
        )
        result = page_drafts.get(DRAFT_UUID)
        assert isinstance(result, PageDraft)
        assert result.id == DRAFT_UUID
        assert result.title == "Draft Page"

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.get("")

    def test_validates_control_chars(self, page_drafts: PageDraftResource) -> None:
        """Control chars in page_draft_id are rejected."""
        with pytest.raises(ValidationError):
            page_drafts.get("draft\x00id")


# =============================================================================
# create() — POST /pagedrafts
# =============================================================================


class TestCreate:
    """Create a new page draft."""

    def test_create_minimal(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Create a page draft with just a title."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=_page_draft_json(),
            status_code=201,
        )
        result = page_drafts.create(title="Draft Page")
        assert isinstance(result, PageDraft)
        assert result.title == "Draft Page"

    def test_create_with_all_fields(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Create with all optional fields sends correct body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=_page_draft_json(page_id=PAGE_UUID),
            status_code=201,
        )
        page_drafts.create(
            title="Full Draft",
            page_id=PAGE_UUID,
            json_content='{"type":"doc"}',
            hero_image="https://example.com/hero.png",
            badge_emoji=":star:",
            parent_page_id=PARENT_UUID,
            knowledge_agent_id=AGENT_UUID,
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["title"] == "Full Draft"
        assert body["pageId"] == PAGE_UUID
        assert body["jsonContent"] == '{"type":"doc"}'
        assert body["heroImage"] == "https://example.com/hero.png"
        assert body["badgeEmoji"] == ":star:"
        assert body["parentPageId"] == PARENT_UUID
        assert body["knowledgeAgentId"] == AGENT_UUID

    def test_create_omits_none_fields(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """None/default fields are not sent in the body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pagedrafts",
            json=_page_draft_json(),
            status_code=201,
        )
        page_drafts.create(title="Simple Draft")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"title": "Simple Draft"}

    def test_create_validates_title(self, page_drafts: PageDraftResource) -> None:
        """Empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.create(title="")


# =============================================================================
# delete() — DELETE /pagedrafts/{pageDraftId}
# =============================================================================


class TestDelete:
    """Delete a page draft."""

    def test_delete(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Delete a page draft by ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}",
            method="DELETE",
            status_code=204,
        )
        page_drafts.delete(DRAFT_UUID)

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.delete("")


# =============================================================================
# list_collaborators() — GET /pagedrafts/{id}/collaborators
# =============================================================================


class TestListCollaborators:
    """List collaborators on a page draft."""

    def test_list_collaborators(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """List returns PageDraftCollaborator objects."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json(), _collaborator_json("c2", "user-group")],
        )
        result = page_drafts.list_collaborators(DRAFT_UUID)
        assert len(result) == 2
        assert isinstance(result[0], PageDraftCollaborator)
        assert result[0].type == "user"
        assert result[0].user is not None
        assert result[0].user.email == "collab@example.com"
        assert result[1].type == "user-group"

    def test_list_collaborators_empty(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """No collaborators returns empty list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators",
            json=[],
        )
        result = page_drafts.list_collaborators(DRAFT_UUID)
        assert result == []

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.list_collaborators("")


# =============================================================================
# add_collaborators() — POST /pagedrafts/{id}/collaborators
# =============================================================================


class TestAddCollaborators:
    """Add collaborators to a page draft."""

    def test_add_collaborators(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Add collaborators returns updated list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json()],
        )
        collabs = [{"type": "user", "objectRole": {"id": "role-1"}}]
        result = page_drafts.add_collaborators(DRAFT_UUID, collabs)
        assert len(result) == 1
        assert isinstance(result[0], PageDraftCollaborator)

    def test_add_collaborators_body(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Verify the request body wraps collaborators."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json()],
        )
        collabs = [{"type": "user"}]
        page_drafts.add_collaborators(DRAFT_UUID, collabs)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "collaborators" in body
        assert body["collaborators"] == collabs

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.add_collaborators("", [])


# =============================================================================
# update_collaborators() — PUT /pagedrafts/{id}/collaborators
# =============================================================================


class TestUpdateCollaborators:
    """Update collaborator roles on a page draft."""

    def test_update_collaborators(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Update collaborators returns updated list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators",
            json=[_collaborator_json()],
        )
        collabs = [{"type": "user", "objectRole": {"id": "role-2"}}]
        result = page_drafts.update_collaborators(DRAFT_UUID, collabs)
        assert len(result) == 1
        assert isinstance(result[0], PageDraftCollaborator)

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.update_collaborators("", [])


# =============================================================================
# remove_collaborator() — DELETE /pagedrafts/{id}/collaborators/{collaboratorId}
# =============================================================================


class TestRemoveCollaborator:
    """Remove a collaborator from a page draft."""

    def test_remove_collaborator(self, page_drafts: PageDraftResource, httpx_mock) -> None:
        """Delete removes a collaborator."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pagedrafts/{DRAFT_UUID}/collaborators/{COLLAB_UUID}",
            method="DELETE",
            status_code=204,
        )
        page_drafts.remove_collaborator(DRAFT_UUID, COLLAB_UUID)

    def test_validates_draft_id(self, page_drafts: PageDraftResource) -> None:
        """Empty page_draft_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.remove_collaborator("", COLLAB_UUID)

    def test_validates_collaborator_id(self, page_drafts: PageDraftResource) -> None:
        """Empty collaborator_id raises ValidationError."""
        with pytest.raises(ValidationError):
            page_drafts.remove_collaborator(DRAFT_UUID, "")
