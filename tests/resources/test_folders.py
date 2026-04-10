"""Tests for guru_sdk.resources.folders — FolderResource.

TDD tests covering the folder API surface:
- CRUD (get, list, create, update, remove)
- Hierarchy (items, parent)
- Permissions (permissions, effective_permissions, add_permission, remove_permission)
- Cross-collection move (move_to_collection)
- Name resolution (accept folder ID or title)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models import (
    EffectivePermissions,
    Folder,
    FolderItem,
)
from guru_sdk.resources.folders import FolderResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

FOLDER_UUID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
FOLDER_UUID_2 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab"
COLLECTION_UUID = "eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee"
GROUP_UUID = "gggggggg-gggg-gggg-gggg-gggggggggggg"
PERMISSION_UUID = "pppppppp-pppp-pppp-pppp-pppppppppppp"


def _folder_json(
    folder_id: str = FOLDER_UUID,
    title: str = "Onboarding",
    home: bool = False,
) -> dict:
    """Build a realistic Folder API response dict."""
    return {
        "id": folder_id,
        "title": title,
        "home": home,
        "collection": {"id": COLLECTION_UUID, "name": "Engineering"},
        "dateCreated": "2025-01-15T10:00:00.000+0000",
        "lastModified": "2025-06-01T14:30:00.000+0000",
    }


def _folder_item_json(item_id: str = "item-1", item_type: str = "card") -> dict:
    """Build a realistic FolderItem API response dict."""
    return {
        "id": item_id,
        "itemId": "card-123",
        "type": item_type,
    }


def _effective_permissions_json() -> dict:
    """Build a realistic EffectivePermissions API response dict."""
    return {
        "owner": {
            "id": "user-1",
            "email": "owner@example.com",
            "firstName": "Test",
            "lastName": "Owner",
        },
        "collectionAccess": [],
    }


def _group_access_json(group_id: str = GROUP_UUID) -> dict:
    """Build a realistic UserGroupAccess API response dict."""
    return {
        "groupId": group_id,
        "groupName": "Engineering Team",
        "role": "AUTHOR",
    }


# =============================================================================
# Fixture
# =============================================================================


@pytest.fixture()
def folders(http_client: HttpClient) -> FolderResource:
    """FolderResource backed by a mock HTTP transport."""
    return FolderResource(http_client)


# =============================================================================
# FolderResource.get() — GET /folders/{id}
# =============================================================================


class TestGet:
    """Get a single folder by ID or title."""

    def test_get_by_uuid(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folder = folders.get(FOLDER_UUID)
        assert isinstance(folder, Folder)
        assert folder.id == FOLDER_UUID

    def test_get_sends_correct_path(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.get(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}"

    def test_get_by_title_resolves(self, folders: FolderResource, httpx_mock) -> None:
        """Non-UUID triggers name resolution: list → match by title → get."""
        httpx_mock.add_response(json=[_folder_json()])
        httpx_mock.add_response(json=_folder_json())
        folder = folders.get("Onboarding")
        assert folder.id == FOLDER_UUID

    def test_get_by_title_case_insensitive(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json()])
        httpx_mock.add_response(json=_folder_json())
        folder = folders.get("onboarding")
        assert folder.id == FOLDER_UUID

    def test_get_by_title_not_found(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json()])
        with pytest.raises(NotFoundError):
            folders.get("Nonexistent")

    def test_get_validates_input(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.get("folder\x00id")


# =============================================================================
# FolderResource.list() — GET /folders
# =============================================================================


class TestList:
    """List all folders."""

    def test_list_returns_folders(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json(), _folder_json(folder_id=FOLDER_UUID_2)])
        result = folders.list()
        assert len(result) == 2
        assert all(isinstance(f, Folder) for f in result)

    def test_list_sends_correct_path(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        folders.list()
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/folders"

    def test_list_with_collection_filter(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json()])
        folders.list(collection_id=COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert f"collection={COLLECTION_UUID}" in str(request.url)

    def test_list_empty(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = folders.list()
        assert result == []


# =============================================================================
# FolderResource.create() — POST /folders
# =============================================================================


class TestCreate:
    """Create a new folder."""

    def test_create_returns_folder(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folder = folders.create(title="Onboarding", collection_id=COLLECTION_UUID)
        assert isinstance(folder, Folder)

    def test_create_sends_correct_body(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.create(title="Onboarding", collection_id=COLLECTION_UUID, description="Welcome docs")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/folders"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["title"] == "Onboarding"
        assert body["collection"]["id"] == COLLECTION_UUID
        assert body["description"] == "Welcome docs"

    def test_create_validates_title(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.create(title="bad\x00title", collection_id=COLLECTION_UUID)

    def test_create_validates_collection_id(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.create(title="OK", collection_id="../escape")


# =============================================================================
# FolderResource.update() — PUT /folders/{id}
# =============================================================================


class TestUpdate:
    """Update an existing folder."""

    def test_update_returns_folder(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json(title="Updated"))
        folder = folders.update(FOLDER_UUID, title="Updated")
        assert folder.title == "Updated"

    def test_update_sends_correct_request(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.update(FOLDER_UUID, title="New Title")
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}"
        assert request.method == "PUT"
        body = json.loads(request.content)
        assert body["title"] == "New Title"

    def test_update_only_sends_provided_fields(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.update(FOLDER_UUID, description="New desc")
        request = httpx_mock.get_request()
        assert request is not None
        body = json.loads(request.content)
        assert "title" not in body
        assert body["description"] == "New desc"


# =============================================================================
# FolderResource.remove() — DELETE /folders/{id}
# =============================================================================


class TestRemove:
    """Delete a folder."""

    def test_remove_sends_delete(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        folders.remove(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}"
        assert request.method == "DELETE"

    def test_remove_with_remove_type(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        folders.remove(FOLDER_UUID, remove_type="FOLDERS_AND_CARDS")
        request = httpx_mock.get_request()
        assert request is not None
        assert "removeType=FOLDERS_AND_CARDS" in str(request.url)

    def test_remove_default_no_remove_type(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        folders.remove(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert "removeType" not in str(request.url)


# =============================================================================
# FolderResource.items() — GET /folders/{id}/items
# =============================================================================


class TestItems:
    """List items in a folder."""

    def test_items_returns_list(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_item_json()])
        result = folders.items(FOLDER_UUID)
        assert len(result) == 1
        assert isinstance(result[0], FolderItem)

    def test_items_empty(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = folders.items(FOLDER_UUID)
        assert result == []

    def test_items_sends_correct_path(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[])
        folders.items(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}/items"


# =============================================================================
# FolderResource.parent() — GET /folders/{id}/parent
# =============================================================================


class TestParent:
    """Get a folder's parent folder."""

    def test_parent_returns_folder(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json(folder_id=FOLDER_UUID_2, title="Parent"))
        result = folders.parent(FOLDER_UUID)
        assert isinstance(result, Folder)
        assert result.id == FOLDER_UUID_2

    def test_parent_sends_correct_path(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.parent(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}/parent"


# =============================================================================
# FolderResource.permissions() — GET /folders/{id}/permissions
# =============================================================================


class TestPermissions:
    """Get folder-level permissions."""

    def test_permissions_returns_list(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_group_access_json()])
        result = folders.permissions(FOLDER_UUID)
        assert len(result) == 1

    def test_permissions_empty(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        result = folders.permissions(FOLDER_UUID)
        assert result == []


# =============================================================================
# FolderResource.effective_permissions() — GET /folders/{id}/effectivepermissions
# =============================================================================


class TestEffectivePermissions:
    """Get effective permissions (resolved through hierarchy)."""

    def test_effective_permissions_returns_model(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_effective_permissions_json())
        result = folders.effective_permissions(FOLDER_UUID)
        assert isinstance(result, EffectivePermissions)

    def test_effective_permissions_sends_correct_path(
        self, folders: FolderResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_effective_permissions_json())
        folders.effective_permissions(FOLDER_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}/effectivepermissions"


# =============================================================================
# FolderResource.add_permission() — POST /folders/{id}/permissions
# =============================================================================


class TestAddPermission:
    """Add a group to folder permissions."""

    def test_add_permission_sends_correct_body(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=200, json={})
        folders.add_permission(FOLDER_UUID, GROUP_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == f"/api/v1/folders/{FOLDER_UUID}/permissions"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["groupId"] == GROUP_UUID
        assert body["role"] == "MEMBER"


# =============================================================================
# FolderResource.remove_permission() — DELETE /folders/{id}/permissions/{permId}
# =============================================================================


class TestRemovePermission:
    """Remove a group from folder permissions."""

    def test_remove_permission_sends_delete(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=204)
        folders.remove_permission(FOLDER_UUID, PERMISSION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == (
            f"/api/v1/folders/{FOLDER_UUID}/permissions/{PERMISSION_UUID}"
        )
        assert request.method == "DELETE"


# =============================================================================
# FolderResource.move_to_collection() — POST /folders/bulkop
# =============================================================================


class TestMoveToCollection:
    """Move a folder to a different collection."""

    def test_move_sends_correct_body(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(status_code=200, json={})
        folders.move_to_collection(FOLDER_UUID, COLLECTION_UUID)
        request = httpx_mock.get_request()
        assert request is not None
        assert request.url.path == "/api/v1/folders/bulkop"
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["action"]["type"] == "move-folder"
        assert body["action"]["collectionId"] == COLLECTION_UUID
        assert FOLDER_UUID in body["items"]["folderIds"]


# =============================================================================
# Name Resolution
# =============================================================================


class TestNameResolution:
    """Name resolution: non-UUID titles resolved via list + match."""

    def test_uuid_skips_resolution(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_folder_json())
        folders.get(FOLDER_UUID)
        requests = httpx_mock.get_requests()
        assert len(requests) == 1

    def test_resolve_case_insensitive(self, folders: FolderResource, httpx_mock) -> None:
        httpx_mock.add_response(json=[_folder_json()])
        httpx_mock.add_response(json=_folder_json())
        folders.get("ONBOARDING")
        assert True  # didn't raise


# =============================================================================
# Input Validation
# =============================================================================


class TestInputValidation:
    """Input validation rejects hallucinated patterns."""

    def test_control_chars(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.get("folder\x00id")

    def test_path_traversal(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.get("../../../etc/passwd")

    def test_remove_validates(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.remove("bad?id")

    def test_items_validates(self, folders: FolderResource) -> None:
        with pytest.raises(ValidationError):
            folders.items("bad%20id")
