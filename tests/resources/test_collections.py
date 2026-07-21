"""Tests for guru_sdk.resources.collections — CollectionResource.

TDD tests covering the collection API surface:
- CRUD (get, list, create, update, remove)
- Group access (groups, add_group, update_group, remove_group)
- Navigation (home_folder)
- Name resolution (accept collection ID or name)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models import CollectionModel, Folder
from guru_sdk.resources.collections import CollectionResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

COLLECTION_UUID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
COLLECTION_UUID_2 = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeee2"
GROUP_UUID = "gggggggg-gggg-gggg-gggg-gggggggggggg"
HOME_FOLDER_UUID = "ffffffff-ffff-ffff-ffff-ffffffffffff"


def _collection_json(
    collection_id: str = COLLECTION_UUID,
    name: str = "Engineering",
) -> dict:
    """Build a realistic Collection API response dict."""
    return {
        "id": collection_id,
        "name": name,
        "color": "#4A90D9",
        "description": "Engineering knowledge base",
        "dateCreated": "2025-01-01T00:00:00.000+0000",
    }


def _group_access_json(group_id: str = GROUP_UUID, role: str = "AUTHOR") -> dict:
    """Build a realistic UserGroupAccess API response dict."""
    return {
        "groupId": group_id,
        "groupName": "Engineering Team",
        "role": role,
    }


def _folder_json() -> dict:
    """Build a realistic non-home folder response (home=False)."""
    return {
        "id": HOME_FOLDER_UUID,
        "title": "Subfolder",
        "home": False,
        "collection": {"id": COLLECTION_UUID, "name": "Engineering"},
    }


def _home_folder_json() -> dict:
    """Build a realistic home folder response."""
    return {
        "id": HOME_FOLDER_UUID,
        "title": "Home",
        "home": True,
        "collection": {"id": COLLECTION_UUID, "name": "Engineering"},
    }


# =============================================================================
# Fixture
# =============================================================================


@pytest.fixture()
def collections(http_client: HttpClient) -> CollectionResource:
    """CollectionResource backed by a mock HTTP transport."""
    return CollectionResource(http_client)


# =============================================================================
# CollectionResource.get() — GET /collections/{id}
# =============================================================================


class TestGet:
    """Get a single collection by ID or name."""

    def test_get_by_uuid(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        coll = collections.get(COLLECTION_UUID)
        assert isinstance(coll, CollectionModel)
        assert coll.id == COLLECTION_UUID
        assert coll.name == "Engineering"

    def test_get_sends_correct_path(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.get(COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/collections/{COLLECTION_UUID}"

    def test_get_by_name_resolves(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        httpx_mock.add_response(json=_collection_json())
        coll = collections.get("Engineering")
        assert coll.id == COLLECTION_UUID

    def test_get_by_name_case_insensitive(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        httpx_mock.add_response(json=_collection_json())
        coll = collections.get("engineering")
        assert coll.id == COLLECTION_UUID

    def test_get_by_name_not_found(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        with pytest.raises(NotFoundError):
            collections.get("Nonexistent")

    def test_get_validates_input(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.get("coll\x00id")


# =============================================================================
# CollectionResource.list() — GET /collections
# =============================================================================


class TestList:
    """List all collections."""

    def test_list_returns_collections(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(
            json=[
                _collection_json(),
                _collection_json(collection_id=COLLECTION_UUID_2, name="Sales"),
            ]
        )
        result = collections.list()
        assert len(result) == 2
        assert all(isinstance(c, CollectionModel) for c in result)

    def test_list_sends_correct_path(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        collections.list()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/collections"

    def test_list_empty(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = collections.list()
        assert result == []


# =============================================================================
# CollectionResource.create() — POST /collections
# =============================================================================


class TestCreate:
    """Create a new collection."""

    def test_create_returns_collection(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        coll = collections.create(name="Engineering")
        assert isinstance(coll, CollectionModel)

    def test_create_sends_correct_body(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.create(name="Engineering", description="Eng KB", color="#4A90D9")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/collections"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["name"] == "Engineering"
        assert body["description"] == "Eng KB"
        assert body["color"] == "#4A90D9"

    def test_create_minimal(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.create(name="Engineering")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert body["name"] == "Engineering"
        assert "description" not in body
        assert "color" not in body

    def test_create_validates_name(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.create(name="bad\x00name")


# =============================================================================
# CollectionResource.update() — PUT /collections/{id}
# =============================================================================


class TestUpdate:
    """Update an existing collection."""

    def test_update_returns_collection(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json(name="Updated"))
        coll = collections.update(COLLECTION_UUID, name="Updated")
        assert coll.name == "Updated"

    def test_update_sends_correct_request(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.update(COLLECTION_UUID, name="New Name", color="#FF0000")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/collections/{COLLECTION_UUID}"
        assert request.method == "PUT"
        body = json.loads(request.content)
        assert body["name"] == "New Name"
        assert body["color"] == "#FF0000"

    def test_update_only_sends_provided_fields(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.update(COLLECTION_UUID, description="New desc")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert "name" not in body
        assert body["description"] == "New desc"


# =============================================================================
# CollectionResource.remove() — DELETE /collections/{id}
# =============================================================================


class TestRemove:
    """Delete a collection."""

    def test_remove_sends_delete(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        collections.remove(COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/collections/{COLLECTION_UUID}"
        assert request.method == "DELETE"

    def test_remove_validates_id(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.remove("../bad")


# =============================================================================
# CollectionResource.groups() — GET /collections/{id}/groups
# =============================================================================


class TestGroups:
    """List groups with access to a collection."""

    def test_groups_returns_list(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_group_access_json()])
        result = collections.groups(COLLECTION_UUID)
        assert len(result) == 1

    def test_groups_empty(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = collections.groups(COLLECTION_UUID)
        assert result == []

    def test_groups_sends_correct_path(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        collections.groups(COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/collections/{COLLECTION_UUID}/groups"


# =============================================================================
# CollectionResource.add_group() — POST /collections/{id}/groups
# =============================================================================


class TestAddGroup:
    """Add a group to a collection."""

    def test_add_group_sends_correct_body(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_group_access_json())
        collections.add_group(COLLECTION_UUID, GROUP_UUID, role="AUTHOR")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/collections/{COLLECTION_UUID}/groups"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["groupId"] == GROUP_UUID
        assert body["role"] == "AUTHOR"

    def test_add_group_validates_inputs(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.add_group("bad?id", GROUP_UUID, role="AUTHOR")
        with pytest.raises(ValidationError):
            collections.add_group(COLLECTION_UUID, "bad%20id", role="AUTHOR")


# =============================================================================
# CollectionResource.update_group() — PUT /collections/{id}/groups/{groupId}
# =============================================================================


class TestUpdateGroup:
    """Update a group's role on a collection."""

    def test_update_group_sends_correct_request(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_group_access_json(role="COLL_ADMIN"))
        collections.update_group(COLLECTION_UUID, GROUP_UUID, role="COLL_ADMIN")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (f"/api/v1/collections/{COLLECTION_UUID}/groups/{GROUP_UUID}")
        assert request.method == "PUT"
        body = json.loads(request.content)
        assert body["role"] == "COLL_ADMIN"


# =============================================================================
# CollectionResource.remove_group() — DELETE /collections/{id}/groups/{groupId}
# =============================================================================


class TestRemoveGroup:
    """Remove a group from a collection."""

    def test_remove_group_sends_delete(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        collections.remove_group(COLLECTION_UUID, GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (f"/api/v1/collections/{COLLECTION_UUID}/groups/{GROUP_UUID}")
        assert request.method == "DELETE"


# =============================================================================
# CollectionResource.home_folder() — find home folder for a collection
# =============================================================================


class TestHomeFolder:
    """Get a collection's home folder."""

    def test_home_folder_returns_folder(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_home_folder_json()])
        result = collections.home_folder(COLLECTION_UUID)
        assert isinstance(result, Folder)
        assert result.home is True

    def test_home_folder_sends_correct_path(
        self, collections: CollectionResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=[_home_folder_json()])
        collections.home_folder(COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert f"collection={COLLECTION_UUID}" in str(request.url)

    def test_home_folder_not_found(self, collections: CollectionResource, httpx_mock) -> None:
        """Raises NotFoundError if no home folder exists."""
        httpx_mock.add_response(json=[_folder_json()])  # not home=True
        with pytest.raises(NotFoundError):
            collections.home_folder(COLLECTION_UUID)


# =============================================================================
# Name Resolution
# =============================================================================


class TestNameResolution:
    """Name resolution: non-UUID names resolved via list + match."""

    def test_uuid_skips_resolution(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_collection_json())
        collections.get(COLLECTION_UUID)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1

    def test_resolve_case_insensitive(self, collections: CollectionResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_collection_json()])
        httpx_mock.add_response(json=_collection_json())
        collections.get("ENGINEERING")
        assert True  # didn't raise


# =============================================================================
# Input Validation
# =============================================================================


class TestInputValidation:
    """Input validation rejects hallucinated patterns."""

    def test_control_chars(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.get("coll\x00id")

    def test_path_traversal(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.get("../../../etc/passwd")

    def test_remove_validates(self, collections: CollectionResource) -> None:
        with pytest.raises(ValidationError):
            collections.remove("bad?id")
