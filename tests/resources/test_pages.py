"""Tests for guru_sdk.resources.pages — PageResource.

TDD tests covering the page API surface:
- list() — list all pages (GET /pages)
- get() — get a page by ID (GET /pages/{pageId})
- list_nested() — get pages in nested tree (GET /pages/nested)
- create() — create a page (POST /pages)
- update() — update a page (PUT /pages/{pageId})
- delete() — delete a page (DELETE /pages/{pageId})
- move() — reposition a page (PUT /pages/{pageId}/position)
- list_permissions() — list page permissions (GET /pages/{pageId}/permissions)
- add_permissions() — add page permissions (POST /pages/{pageId}/permissions)
- update_permission() — update a page permission (PUT /pages/{pageId}/permissions/{permId})
- remove_permission() — remove a page permission (DELETE /pages/{pageId}/permissions/{permId})
- Input validation

All endpoints are internal API (not in public Swagger) — mirrors guru-cli ADR-014.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import Page
from guru_sdk.models._manual import PagePermission
from guru_sdk.resources.pages import PageResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

PAGE_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
PAGE_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
CHILD_PAGE_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
AGENT_UUID = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"
DRAFT_UUID = "e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5"
PERM_UUID = "f6f6f6f6-f6f6-f6f6-f6f6-f6f6f6f6f6f6"


def _page_json(
    page_id: str = PAGE_UUID,
    title: str = "Getting Started",
    *,
    parent_page_id: str | None = None,
    sub_pages: list[dict] | None = None,
) -> dict:
    """Build a realistic Page API response dict."""
    result: dict = {
        "id": page_id,
        "title": title,
        "jsonContent": '{"type":"doc","content":[]}',
        "heroImage": "https://example.com/hero.png",
        "badgeEmoji": ":star:",
        "draft": False,
        "editable": True,
        "onlyNavigable": False,
        "dateCreated": "2025-06-01T10:00:00.000+0000",
        "lastModified": "2025-06-15T14:30:00.000+0000",
        "lastModifiedBy": {
            "email": "editor@example.com",
            "firstName": "Page",
            "lastName": "Editor",
        },
        "team": {
            "id": "t1t1t1t1-t1t1-t1t1-t1t1-t1t1t1t1t1t1",
            "dateCreated": "2025-01-01T00:00:00.000+0000",
        },
    }
    if parent_page_id is not None:
        result["parentPageId"] = parent_page_id
    if sub_pages is not None:
        result["subPages"] = sub_pages
    return result


def _permission_json(
    perm_id: str = PERM_UUID,
    perm_type: str = "user-group",
    permission_type: str = "EDITOR",
) -> dict:
    """Build a page permission response dict."""
    return {
        "id": perm_id,
        "type": perm_type,
        "permissionType": permission_type,
        "objectRole": {"id": "role-1", "name": "Author"},
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def pages(http_client: HttpClient) -> PageResource:
    """PageResource wired to the mock HttpClient."""
    return PageResource(http_client)


# =============================================================================
# list() — GET /pages
# =============================================================================


class TestList:
    """List all pages."""

    def test_list_all(self, pages: PageResource, httpx_mock) -> None:
        """List pages returns list of Page objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=[
                _page_json(PAGE_UUID, "Getting Started"),
                _page_json(PAGE_UUID_2, "API Reference"),
            ],
        )
        result = pages.list()
        assert len(result) == 2
        assert isinstance(result[0], Page)
        assert result[0].title == "Getting Started"
        assert result[1].title == "API Reference"

    def test_list_empty(self, pages: PageResource, httpx_mock) -> None:
        """No pages returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=[],
        )
        result = pages.list()
        assert result == []

    def test_page_nested_fields(self, pages: PageResource, httpx_mock) -> None:
        """Page model parses nested team and lastModifiedBy."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=[_page_json()],
        )
        result = pages.list()
        page = result[0]
        assert page.last_modified_by is not None
        assert page.last_modified_by.email == "editor@example.com"
        assert page.team is not None
        assert page.team.id == "t1t1t1t1-t1t1-t1t1-t1t1-t1t1t1t1t1t1"


# =============================================================================
# get() — GET /pages/{pageId}
# =============================================================================


class TestGet:
    """Get a page by ID."""

    def test_get_by_id(self, pages: PageResource, httpx_mock) -> None:
        """Get a page by UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}",
            json=_page_json(),
        )
        result = pages.get(PAGE_UUID)
        assert isinstance(result, Page)
        assert result.id == PAGE_UUID
        assert result.title == "Getting Started"

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.get("")

    def test_validates_control_chars(self, pages: PageResource) -> None:
        """Control chars in page_id are rejected."""
        with pytest.raises(ValidationError):
            pages.get("page\x00id")


# =============================================================================
# list_nested() — GET /pages/nested
# =============================================================================


class TestListNested:
    """Get pages in nested tree structure."""

    def test_nested_tree(self, pages: PageResource, httpx_mock) -> None:
        """Returns root page with sub_pages tree."""
        child = _page_json(CHILD_PAGE_UUID, "Child Page", parent_page_id=PAGE_UUID)
        root = _page_json(PAGE_UUID, "Root", sub_pages=[child])
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages/nested",
            json=root,
        )
        result = pages.list_nested()
        assert isinstance(result, Page)
        assert result.title == "Root"
        assert result.sub_pages is not None
        assert len(result.sub_pages) == 1
        assert result.sub_pages[0].title == "Child Page"

    def test_nested_view_only(self, pages: PageResource, httpx_mock) -> None:
        """view_only=True passes query param."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages/nested?viewOnly=true",
            json=_page_json(),
        )
        result = pages.list_nested(view_only=True)
        assert isinstance(result, Page)


# =============================================================================
# create() — POST /pages
# =============================================================================


class TestCreate:
    """Create a new page."""

    def test_create_minimal(self, pages: PageResource, httpx_mock) -> None:
        """Create a page with just a title."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=_page_json(),
            status_code=201,
        )
        result = pages.create(title="Getting Started")
        assert isinstance(result, Page)
        assert result.title == "Getting Started"

    def test_create_sends_body(self, pages: PageResource, httpx_mock) -> None:
        """Create sends all provided fields in the POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=_page_json(),
            status_code=201,
        )
        pages.create(
            title="New Page",
            json_content='{"type":"doc"}',
            hero_image="https://example.com/hero.png",
            badge_emoji=":star:",
            parent_page_id=PAGE_UUID_2,
            knowledge_agent_id=AGENT_UUID,
            draft_id=DRAFT_UUID,
            only_navigable=True,
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["title"] == "New Page"
        assert body["jsonContent"] == '{"type":"doc"}'
        assert body["heroImage"] == "https://example.com/hero.png"
        assert body["badgeEmoji"] == ":star:"
        assert body["parentPageId"] == PAGE_UUID_2
        assert body["knowledgeAgentId"] == AGENT_UUID
        assert body["draftId"] == DRAFT_UUID
        assert body["onlyNavigable"] is True

    def test_create_omits_none_fields(self, pages: PageResource, httpx_mock) -> None:
        """None/default fields are not sent in the body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/pages",
            json=_page_json(),
            status_code=201,
        )
        pages.create(title="Simple Page")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"title": "Simple Page"}

    def test_create_validates_title(self, pages: PageResource) -> None:
        """Empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.create(title="")

    def test_create_validates_parent_page_id(self, pages: PageResource) -> None:
        """Invalid parent_page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.create(title="Test", parent_page_id="page\x00id")


# =============================================================================
# update() — PUT /pages/{pageId}
# =============================================================================


class TestUpdate:
    """Update an existing page."""

    def test_update(self, pages: PageResource, httpx_mock) -> None:
        """Update a page returns updated Page."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}",
            json=_page_json(title="Updated Title"),
        )
        result = pages.update(PAGE_UUID, title="Updated Title")
        assert isinstance(result, Page)
        assert result.title == "Updated Title"

    def test_update_sends_body(self, pages: PageResource, httpx_mock) -> None:
        """Update sends only provided fields."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}",
            json=_page_json(),
        )
        pages.update(
            PAGE_UUID,
            title="New Title",
            json_content='{"type":"doc"}',
            knowledge_agent_id=AGENT_UUID,
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["title"] == "New Title"
        assert body["jsonContent"] == '{"type":"doc"}'
        assert body["knowledgeAgentId"] == AGENT_UUID
        assert "heroImage" not in body

    def test_update_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.update("", title="Test")


# =============================================================================
# delete() — DELETE /pages/{pageId}
# =============================================================================


class TestDelete:
    """Delete a page."""

    def test_delete(self, pages: PageResource, httpx_mock) -> None:
        """Delete a page by ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}",
            method="DELETE",
            status_code=204,
        )
        pages.delete(PAGE_UUID)

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.delete("")


# =============================================================================
# move() — PUT /pages/{pageId}/position
# =============================================================================


class TestMove:
    """Move a page to a new position in the hierarchy."""

    def test_move_to_parent(self, pages: PageResource, httpx_mock) -> None:
        """Move a page under a new parent."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{CHILD_PAGE_UUID}/position",
            json=_page_json(CHILD_PAGE_UUID, "Moved Page", parent_page_id=PAGE_UUID_2),
        )
        result = pages.move(CHILD_PAGE_UUID, parent_page_id=PAGE_UUID_2)
        assert isinstance(result, Page)
        assert result.parent_page_id == PAGE_UUID_2

    def test_move_with_sibling(self, pages: PageResource, httpx_mock) -> None:
        """Move a page after a sibling."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{CHILD_PAGE_UUID}/position",
            json=_page_json(CHILD_PAGE_UUID, "Moved Page"),
        )
        pages.move(
            CHILD_PAGE_UUID,
            parent_page_id=PAGE_UUID,
            prev_sibling_page_id=PAGE_UUID_2,
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["parentPageId"] == PAGE_UUID
        assert body["prevSiblingPageId"] == PAGE_UUID_2

    def test_move_to_first(self, pages: PageResource, httpx_mock) -> None:
        """Move to first position — prevSiblingPageId='first' is not validated as ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{CHILD_PAGE_UUID}/position",
            json=_page_json(CHILD_PAGE_UUID, "First Page"),
        )
        pages.move(CHILD_PAGE_UUID, prev_sibling_page_id="first")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["prevSiblingPageId"] == "first"

    def test_move_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.move("", parent_page_id=PAGE_UUID)


# =============================================================================
# list_permissions() — GET /pages/{pageId}/permissions
# =============================================================================


class TestListPermissions:
    """List permissions on a page."""

    def test_list_permissions(self, pages: PageResource, httpx_mock) -> None:
        """List returns PagePermission objects."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions",
            json=[_permission_json(), _permission_json("p2", "user", "VIEWER")],
        )
        result = pages.list_permissions(PAGE_UUID)
        assert len(result) == 2
        assert isinstance(result[0], PagePermission)
        assert result[0].type == "user-group"
        assert result[0].permission_type == "EDITOR"
        assert result[1].type == "user"
        assert result[1].permission_type == "VIEWER"

    def test_list_permissions_empty(self, pages: PageResource, httpx_mock) -> None:
        """No permissions returns empty list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions",
            json=[],
        )
        result = pages.list_permissions(PAGE_UUID)
        assert result == []

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.list_permissions("")


# =============================================================================
# add_permissions() — POST /pages/{pageId}/permissions
# =============================================================================


class TestAddPermissions:
    """Add permissions to a page."""

    def test_add_permissions(self, pages: PageResource, httpx_mock) -> None:
        """Add permissions sends list and returns updated permissions."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions",
            json=[_permission_json()],
        )
        perms = [{"type": "user-group", "permissionType": "EDITOR"}]
        result = pages.add_permissions(PAGE_UUID, perms)
        assert len(result) == 1
        assert isinstance(result[0], PagePermission)

    def test_add_permissions_body(self, pages: PageResource, httpx_mock) -> None:
        """Verify the request body wraps permissions in an object."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions",
            json=[_permission_json()],
        )
        perms = [{"type": "user-group", "permissionType": "EDITOR"}]
        pages.add_permissions(PAGE_UUID, perms)
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "permissions" in body
        assert body["permissions"] == perms

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.add_permissions("", [])


# =============================================================================
# update_permission() — PUT /pages/{pageId}/permissions/{permId}
# =============================================================================


class TestUpdatePermission:
    """Update a single permission on a page."""

    def test_update_permission(self, pages: PageResource, httpx_mock) -> None:
        """Update sends permission body via PUT."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions/{PERM_UUID}",
            method="PUT",
            status_code=204,
        )
        perm = {"type": "user-group", "permissionType": "VIEWER"}
        pages.update_permission(PAGE_UUID, PERM_UUID, perm)

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.update_permission("", PERM_UUID, {})

    def test_validates_permission_id(self, pages: PageResource) -> None:
        """Empty permission_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.update_permission(PAGE_UUID, "", {})


# =============================================================================
# remove_permission() — DELETE /pages/{pageId}/permissions/{permId}
# =============================================================================


class TestRemovePermission:
    """Remove a permission from a page."""

    def test_remove_permission(self, pages: PageResource, httpx_mock) -> None:
        """Delete removes a permission."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/pages/{PAGE_UUID}/permissions/{PERM_UUID}",
            method="DELETE",
            status_code=204,
        )
        pages.remove_permission(PAGE_UUID, PERM_UUID)

    def test_validates_page_id(self, pages: PageResource) -> None:
        """Empty page_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.remove_permission("", PERM_UUID)

    def test_validates_permission_id(self, pages: PageResource) -> None:
        """Empty permission_id raises ValidationError."""
        with pytest.raises(ValidationError):
            pages.remove_permission(PAGE_UUID, "")
