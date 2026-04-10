"""Tests for guru_sdk.resources.tags — TagResource.

TDD tests covering the tag API surface:
- Tag CRUD (get_tag, create_tag, update_tag)
- Category CRUD (list_categories, create_category, update_category, delete_category)
- Tag name resolution
- Team ID resolution (via whoami)
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import NotFoundError, ValidationError
from guru_sdk.models import Tag, TagCategory
from guru_sdk.resources.tags import TagResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

TEAM_ID = "tttttttt-tttt-tttt-tttt-tttttttttttt"
TAG_UUID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
TAG_UUID_2 = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaab"
CATEGORY_UUID = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"


def _whoami_json(team_id: str = TEAM_ID) -> dict:
    """Build a realistic WhoAmI response for team ID extraction."""
    return {
        "team": {
            "id": team_id,
            "name": "Test Team",
        },
        "user": {
            "email": "test@example.com",
            "firstName": "Test",
            "lastName": "User",
        },
        "tokenType": "API",
    }


def _tag_json(tag_id: str = TAG_UUID, value: str = "onboarding") -> dict:
    """Build a realistic Tag API response dict."""
    return {
        "id": tag_id,
        "value": value,
        "categoryId": CATEGORY_UUID,
        "categoryName": "Tags",
    }


def _category_json(
    category_id: str = CATEGORY_UUID,
    name: str = "Tags",
    tags: list[dict] | None = None,
) -> dict:
    """Build a realistic TagCategory API response dict."""
    return {
        "id": category_id,
        "name": name,
        "dateCreated": "2025-01-01T00:00:00.000+0000",
        "defaultCategory": name == "Tags",
        "tags": tags or [_tag_json()],
    }


# =============================================================================
# Fixture
# =============================================================================


@pytest.fixture()
def tags(http_client: HttpClient) -> TagResource:
    """TagResource backed by a mock HTTP transport."""
    return TagResource(http_client)


# =============================================================================
# TagResource.list_categories() — GET /teams/{teamId}/tagcategories
# =============================================================================


class TestListCategories:
    """List all tag categories with their tags."""

    def test_list_categories_returns_list(self, tags: TagResource, httpx_mock) -> None:
        # whoami call for team ID
        httpx_mock.add_response(json=_whoami_json())
        # list categories call
        httpx_mock.add_response(json=[_category_json()])
        result = tags.list_categories()
        assert len(result) == 1
        assert isinstance(result[0], TagCategory)
        assert result[0].name == "Tags"

    def test_list_categories_sends_correct_path(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=[_category_json()])
        tags.list_categories()
        requests = httpx_mock.get_requests()
        # First request: whoami, second: list categories
        assert len(requests) == 2
        assert f"/teams/{TEAM_ID}/tagcategories" in requests[1].url.path

    def test_list_categories_caches_team_id(self, tags: TagResource, httpx_mock) -> None:
        """Team ID should be cached after the first call."""
        # First call: whoami + list
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=[_category_json()])
        tags.list_categories()
        # Second call: only list (no whoami)
        httpx_mock.add_response(json=[_category_json()])
        tags.list_categories()
        requests = httpx_mock.get_requests()
        # 3 total: 1 whoami + 2 list calls
        assert len(requests) == 3


# =============================================================================
# TagResource.get_tag() — GET /teams/{teamId}/tagcategories/tags/{tagId}
# =============================================================================


class TestGetTag:
    """Get a single tag by ID."""

    def test_get_tag_returns_tag(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json())
        result = tags.get_tag(TAG_UUID)
        assert isinstance(result, Tag)
        assert result.value == "onboarding"

    def test_get_tag_sends_correct_path(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json())
        tags.get_tag(TAG_UUID)
        requests = httpx_mock.get_requests()
        assert f"/teams/{TEAM_ID}/tagcategories/tags/{TAG_UUID}" in requests[1].url.path

    def test_get_tag_validates_input(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.get_tag("bad%20id")


# =============================================================================
# TagResource.create_tag() — POST /teams/{teamId}/tagcategories/tags
# =============================================================================


class TestCreateTag:
    """Create a new tag."""

    def test_create_tag_returns_tag(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json())
        result = tags.create_tag(category_id=CATEGORY_UUID, value="onboarding")
        assert isinstance(result, Tag)

    def test_create_tag_sends_correct_body(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json())
        tags.create_tag(category_id=CATEGORY_UUID, value="onboarding")
        requests = httpx_mock.get_requests()
        request = requests[1]
        assert request.method == "POST"
        body = json.loads(request.content)
        assert body["categoryId"] == CATEGORY_UUID
        assert body["value"] == "onboarding"

    def test_create_tag_validates_value(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.create_tag(category_id=CATEGORY_UUID, value="bad\x00value")


# =============================================================================
# TagResource.update_tag() — PUT /teams/{teamId}/tagcategories/tags/{tagId}
# =============================================================================


class TestUpdateTag:
    """Update a tag's display value."""

    def test_update_tag_returns_tag(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json(value="new-value"))
        result = tags.update_tag(TAG_UUID, value="new-value")
        assert isinstance(result, Tag)
        assert result.value == "new-value"

    def test_update_tag_sends_correct_request(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_tag_json(value="new-value"))
        tags.update_tag(TAG_UUID, value="new-value")
        requests = httpx_mock.get_requests()
        request = requests[1]
        assert request.method == "PUT"
        assert f"/tags/{TAG_UUID}" in request.url.path
        body = json.loads(request.content)
        assert body["value"] == "new-value"

    def test_update_tag_validates_input(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.update_tag("bad%20id", value="ok")


# =============================================================================
# TagResource.create_category() — POST /teams/{teamId}/tagcategories
# =============================================================================


class TestCreateCategory:
    """Create a new tag category."""

    def test_create_category_returns_category(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_category_json(name="Priority"))
        result = tags.create_category(name="Priority")
        assert isinstance(result, TagCategory)
        assert result.name == "Priority"

    def test_create_category_sends_correct_body(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_category_json(name="Priority"))
        tags.create_category(name="Priority")
        requests = httpx_mock.get_requests()
        request = requests[1]
        assert request.method == "POST"
        assert "/tagcategories" in request.url.path
        body = json.loads(request.content)
        assert body["name"] == "Priority"

    def test_create_category_validates_name(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.create_category(name="bad\x00name")


# =============================================================================
# TagResource.update_category() — PUT /teams/{teamId}/tagcategories/{categoryId}
# =============================================================================


class TestUpdateCategory:
    """Update a tag category's name."""

    def test_update_category_returns_category(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_category_json(name="New Name"))
        result = tags.update_category(CATEGORY_UUID, name="New Name")
        assert isinstance(result, TagCategory)

    def test_update_category_sends_correct_request(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=_category_json(name="New Name"))
        tags.update_category(CATEGORY_UUID, name="New Name")
        requests = httpx_mock.get_requests()
        request = requests[1]
        assert request.method == "PUT"
        assert f"/tagcategories/{CATEGORY_UUID}" in request.url.path

    def test_update_category_validates_input(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.update_category("bad%20id", name="ok")


# =============================================================================
# TagResource.delete_category() — DELETE /teams/{teamId}/tagcategories/{categoryId}
# =============================================================================


class TestDeleteCategory:
    """Delete a tag category and all its tags."""

    def test_delete_category_sends_correct_request(
        self, tags: TagResource, httpx_mock
    ) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(status_code=204)
        tags.delete_category(CATEGORY_UUID)
        requests = httpx_mock.get_requests()
        request = requests[1]
        assert request.method == "DELETE"
        assert f"/tagcategories/{CATEGORY_UUID}" in request.url.path

    def test_delete_category_validates_input(self, tags: TagResource) -> None:
        with pytest.raises(ValidationError):
            tags.delete_category("bad%20id")


# =============================================================================
# Tag Name Resolution
# =============================================================================


class TestTagNameResolution:
    """Resolve tag by name (searches all categories)."""

    def test_resolve_tag_by_name(self, tags: TagResource, httpx_mock) -> None:
        """Non-UUID values resolve by searching categories."""
        httpx_mock.add_response(json=_whoami_json())
        # List categories for resolution
        httpx_mock.add_response(
            json=[_category_json(tags=[_tag_json(), _tag_json(TAG_UUID_2, "offboarding")])]
        )
        # get_tag after resolution
        httpx_mock.add_response(json=_tag_json())
        result = tags.get_tag("onboarding")
        assert isinstance(result, Tag)

    def test_resolve_tag_not_found(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(json=[_category_json()])
        with pytest.raises(NotFoundError):
            tags.get_tag("nonexistent")

    def test_resolve_tag_case_insensitive(self, tags: TagResource, httpx_mock) -> None:
        httpx_mock.add_response(json=_whoami_json())
        httpx_mock.add_response(
            json=[_category_json(tags=[_tag_json(value="Onboarding")])]
        )
        httpx_mock.add_response(json=_tag_json(value="Onboarding"))
        result = tags.get_tag("onboarding")
        assert isinstance(result, Tag)
