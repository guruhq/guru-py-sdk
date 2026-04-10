"""Tests for guru_sdk.resources.groups — GroupResource.

TDD tests covering the group API surface:
- CRUD (get, list, create, update, remove)
- Member management (members, add_members, remove_member)
- Collection access (collections)
- Name resolution (accept group ID or name)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from urllib.parse import unquote

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models import UserGroup, UserGroupMember
from guru_sdk.models._generated import CollectionModel
from guru_sdk.resources.groups import GroupResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

GROUP_UUID = "a0a0a0a0-a0a0-a0a0-a0a0-a0a0a0a0a0a0"
GROUP_UUID_2 = "b1b1b1b1-b1b1-b1b1-b1b1-b1b1b1b1b1b1"
COLLECTION_UUID = "c2c2c2c2-c2c2-c2c2-c2c2-c2c2c2c2c2c2"


def _group_json(
    group_id: str = GROUP_UUID,
    name: str = "Engineering",
) -> dict:
    """Build a realistic UserGroup API response dict."""
    return {
        "id": group_id,
        "name": name,
        "dateCreated": "2025-01-01T00:00:00.000+0000",
        "numberOfMembers": 5,
        "modifiable": True,
    }


def _member_json(email: str = "alice@example.com") -> dict:
    """Build a realistic UserGroupMember API response dict."""
    return {
        "id": "member-1",
        "dateCreated": "2025-01-01T00:00:00.000+0000",
        "user": {
            "email": email,
            "firstName": "Alice",
            "lastName": "Smith",
        },
    }


def _collection_json(collection_id: str = COLLECTION_UUID) -> dict:
    """Build a realistic Collection API response dict."""
    return {
        "id": collection_id,
        "name": "Engineering",
        "color": "#4A90D9",
    }


# =============================================================================
# Fixture
# =============================================================================


@pytest.fixture()
def groups(http_client: HttpClient) -> GroupResource:
    """GroupResource backed by a mock HTTP transport."""
    return GroupResource(http_client)


# =============================================================================
# GroupResource.get() — GET /groups/{id}
# =============================================================================


class TestGet:
    """Get a single group by ID or name."""

    def test_get_returns_group(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json())
        result = groups.get(GROUP_UUID)
        assert isinstance(result, UserGroup)
        assert result.name == "Engineering"

    def test_get_sends_correct_path(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json())
        groups.get(GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}"

    def test_get_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.get("bad%20id")


# =============================================================================
# GroupResource.list() — GET /groups
# =============================================================================


class TestList:
    """List all groups."""

    def test_list_returns_groups(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_group_json(), _group_json(GROUP_UUID_2, "Design")])
        result = groups.list()
        assert len(result) == 2
        assert all(isinstance(g, UserGroup) for g in result)

    def test_list_sends_correct_path(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        groups.list()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/groups"


# =============================================================================
# GroupResource.create() — POST /groups
# =============================================================================


class TestCreate:
    """Create a new group."""

    def test_create_returns_group(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json())
        result = groups.create(name="Engineering")
        assert isinstance(result, UserGroup)
        assert result.name == "Engineering"

    def test_create_sends_correct_body(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json())
        groups.create(name="Engineering")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["name"] == "Engineering"

    def test_create_validates_name(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.create(name="bad\x00name")


# =============================================================================
# GroupResource.update() — PUT /groups/{id}
# =============================================================================


class TestUpdate:
    """Update a group (rename)."""

    def test_update_returns_group(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json(name="New Name"))
        result = groups.update(GROUP_UUID, name="New Name")
        assert isinstance(result, UserGroup)
        assert result.name == "New Name"

    def test_update_sends_correct_request(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json(name="New Name"))
        groups.update(GROUP_UUID, name="New Name")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "PUT"
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}"
        body = json.loads(request.content)
        assert body["name"] == "New Name"

    def test_update_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.update("bad%20id", name="New Name")


# =============================================================================
# GroupResource.remove() — DELETE /groups/{id}
# =============================================================================


class TestRemove:
    """Delete a group."""

    def test_remove_sends_delete(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        groups.remove(GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}"

    def test_remove_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.remove("bad%20id")


# =============================================================================
# GroupResource.members() — GET /groups/{id}/members (paginated)
# =============================================================================


class TestMembers:
    """List members of a group."""

    def test_members_returns_list(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_member_json()])
        result = groups.members(GROUP_UUID)
        assert len(result) == 1
        assert isinstance(result[0], UserGroupMember)
        assert result[0].user.email == "alice@example.com"

    def test_members_sends_correct_path(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_member_json()])
        groups.members(GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}/members"

    def test_members_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.members("bad%20id")


# =============================================================================
# GroupResource.add_members() — POST /groups/{id}/members
# =============================================================================


class TestAddMembers:
    """Add members to a group by email."""

    def test_add_members_sends_correct_request(
        self, groups: GroupResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(status_code=204)
        groups.add_members(GROUP_UUID, emails=["alice@example.com", "bob@example.com"])
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "POST"
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}/members"
        body = json.loads(request.content)
        assert body == [
            {"id": "alice@example.com"},
            {"id": "bob@example.com"},
        ]

    def test_add_members_validates_group_id(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.add_members("bad%20id", emails=["alice@example.com"])


# =============================================================================
# GroupResource.remove_member() — DELETE /groups/{id}/members/{email}
# =============================================================================


class TestRemoveMember:
    """Remove a member from a group."""

    def test_remove_member_sends_correct_request(
        self, groups: GroupResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(status_code=204)
        groups.remove_member(GROUP_UUID, email="alice@example.com")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.method == "DELETE"
        # Email should be percent-encoded in the URL path
        path = unquote(request.url.path)
        assert path == f"/api/v1/groups/{GROUP_UUID}/members/alice@example.com"

    def test_remove_member_validates_group_id(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.remove_member("bad%20id", email="alice@example.com")


# =============================================================================
# GroupResource.collections() — GET /groups/{id}/collections
# =============================================================================


class TestCollections:
    """List collections a group has access to."""

    def test_collections_returns_list(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        result = groups.collections(GROUP_UUID)
        assert len(result) == 1
        assert isinstance(result[0], CollectionModel)

    def test_collections_sends_correct_path(
        self, groups: GroupResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        groups.collections(GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/groups/{GROUP_UUID}/collections"

    def test_collections_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.collections("bad%20id")


# =============================================================================
# Name Resolution
# =============================================================================


class TestNameResolution:
    """Name resolution: non-UUID names resolved via list + match."""

    def test_uuid_skips_resolution(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_group_json())
        groups.get(GROUP_UUID)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1

    def test_resolve_case_insensitive(self, groups: GroupResource, httpx_mock) -> None:
        # First call: list groups for resolution
        httpx_mock.add_response(json=[_group_json()])
        # Second call: get by resolved UUID
        httpx_mock.add_response(json=_group_json())
        groups.get("engineering")
        requests = httpx_mock.get_requests()
        assert len(requests) == 2

    def test_resolve_not_found_raises(self, groups: GroupResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_group_json()])
        with pytest.raises(NotFoundError):
            groups.get("Nonexistent")

    def test_resolve_validates_input(self, groups: GroupResource) -> None:
        with pytest.raises(ValidationError):
            groups.get("bad%20id")
