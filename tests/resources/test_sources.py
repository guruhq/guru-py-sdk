"""Tests for guru_sdk.resources.sources — SourceResource.

TDD tests covering the source API surface:
- list() — list all sources (GET /sources)
- get() — get a specific source (GET /sources/{sourceId})
- object_types() — list object types for a source (GET /sources/{sourceId}/objecttypes)
- connections() — list grouped source connections (GET /sources/groups)
- get_connection() — get a single grouped connection (GET /sources/groups/{groupId})
- Input validation
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import (
    GroupedSourceConnection,
    ObjectType,
    Source,
)
from guru_sdk.resources.sources import SourceResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

SOURCE_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
SOURCE_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
CONNECTION_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
OBJECT_TYPE_UUID = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"


def _source_json(
    source_id: str = SOURCE_UUID,
    name: str = "Confluence",
) -> dict:
    """Build a realistic Source API response dict."""
    return {
        "id": source_id,
        "name": name,
        "description": "Engineering wiki",
        "syncStatus": "SYNCED",
        "lastSyncedDate": "2025-06-15T10:00:00.000+0000",
        "iconUrl": "https://app.getguru.com/icons/confluence.png",
        "connectionId": "conn-123",
        "connectionName": "Confluence Cloud",
        "definition": {
            "id": "def-confluence",
            "name": "Confluence",
            "type": "CONFLUENCE",
        },
        "createdBy": {
            "email": "admin@example.com",
            "firstName": "Admin",
            "lastName": "User",
        },
        "objectSyncs": [
            {
                "objectType": {
                    "id": OBJECT_TYPE_UUID,
                    "name": "Pages",
                },
                "syncStatus": "SYNCED",
            }
        ],
    }


def _object_type_json(
    type_id: str = OBJECT_TYPE_UUID,
    name: str = "Pages",
) -> dict:
    """Build a realistic ObjectType API response dict."""
    return {
        "id": type_id,
        "name": name,
        "externalId": "page",
        "facets": [
            {
                "id": "facet-space",
                "name": "Space",
                "type": "FIELD",
                "hierarchical": False,
                "dataType": "TEXT",
            }
        ],
        "fields": [
            {
                "id": "field-title",
                "name": "Title",
                "externalId": "title",
                "dataType": "TEXT",
            }
        ],
    }


def _grouped_connection_json(
    group_id: str = CONNECTION_UUID,
    name: str = "Confluence",
) -> dict:
    """Build a realistic GroupedSourceConnection API response dict."""
    return {
        "id": group_id,
        "name": name,
        "sourceDefinition": {
            "id": "def-confluence",
            "name": "Confluence",
        },
        "sourceCount": 2,
        "connectionIssuesCount": 0,
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def sources(http_client: HttpClient) -> SourceResource:
    """SourceResource wired to the mock HttpClient."""
    return SourceResource(http_client)


# =============================================================================
# list() — GET /sources
# =============================================================================


class TestList:
    """List all sources."""

    def test_returns_sources(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Basic list returns list of Source objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/sources",
            json=[
                _source_json(SOURCE_UUID, "Confluence"),
                _source_json(SOURCE_UUID_2, "Jira"),
            ],
        )
        result = sources.list()
        assert len(result) == 2
        assert isinstance(result[0], Source)
        assert result[0].name == "Confluence"
        assert result[1].name == "Jira"

    def test_empty_list(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """No sources returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/sources",
            json=[],
        )
        result = sources.list()
        assert result == []

    def test_source_nested_fields(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Source model correctly parses nested definition and createdBy."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/sources",
            json=[_source_json()],
        )
        result = sources.list()
        src = result[0]
        assert src.definition is not None
        assert src.definition.name == "Confluence"
        assert src.created_by is not None
        assert src.created_by.email == "admin@example.com"


# =============================================================================
# get() — GET /sources/{sourceId}
# =============================================================================


class TestGet:
    """Get a source by ID."""

    def test_get_by_id(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Get a specific source by UUID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/{SOURCE_UUID}",
            json=_source_json(),
        )
        result = sources.get(SOURCE_UUID)
        assert isinstance(result, Source)
        assert result.id == SOURCE_UUID
        assert result.name == "Confluence"
        assert result.sync_status.value == "SYNCED"

    def test_validates_source_id(self, sources: SourceResource) -> None:
        """Empty source_id raises ValidationError."""
        with pytest.raises(ValidationError):
            sources.get("")

    def test_validates_control_chars(self, sources: SourceResource) -> None:
        """Control chars in source_id are rejected."""
        with pytest.raises(ValidationError):
            sources.get("source\x00id")


# =============================================================================
# object_types() — GET /sources/{sourceId}/objecttypes
# =============================================================================


class TestObjectTypes:
    """List object types for a source."""

    def test_returns_object_types(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Returns list of ObjectType with facets and fields."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/{SOURCE_UUID}/objecttypes",
            json=[_object_type_json()],
        )
        result = sources.object_types(SOURCE_UUID)
        assert len(result) == 1
        assert isinstance(result[0], ObjectType)
        assert result[0].name == "Pages"
        assert result[0].external_id == "page"

    def test_facets_parsed(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """ObjectType.facets are parsed into ObjectFacet models."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/{SOURCE_UUID}/objecttypes",
            json=[_object_type_json()],
        )
        result = sources.object_types(SOURCE_UUID)
        facets = result[0].facets
        assert facets is not None
        assert len(facets) == 1
        assert facets[0].name == "Space"

    def test_fields_parsed(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """ObjectType.fields are parsed into ObjectField models."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/{SOURCE_UUID}/objecttypes",
            json=[_object_type_json()],
        )
        result = sources.object_types(SOURCE_UUID)
        fields = result[0].fields
        assert fields is not None
        assert len(fields) == 1
        assert fields[0].name == "Title"

    def test_empty_object_types(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Source with no object types returns empty list."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/{SOURCE_UUID}/objecttypes",
            json=[],
        )
        result = sources.object_types(SOURCE_UUID)
        assert result == []

    def test_validates_source_id(self, sources: SourceResource) -> None:
        """Empty source_id raises ValidationError."""
        with pytest.raises(ValidationError):
            sources.object_types("")


# =============================================================================
# connections() — GET /sources/groups
# =============================================================================


class TestConnections:
    """List grouped source connections."""

    def test_returns_connections(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Returns list of GroupedSourceConnection objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/sources/groups",
            json=[
                _grouped_connection_json(CONNECTION_UUID, "Confluence"),
                _grouped_connection_json("e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5", "Jira"),
            ],
        )
        result = sources.connections()
        assert len(result) == 2
        assert isinstance(result[0], GroupedSourceConnection)
        assert result[0].name == "Confluence"
        assert result[0].source_count == 2

    def test_empty_connections(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """No connections returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/sources/groups",
            json=[],
        )
        result = sources.connections()
        assert result == []


# =============================================================================
# get_connection() — GET /sources/groups/{groupId}
# =============================================================================


class TestGetConnection:
    """Get a single grouped source connection."""

    def test_get_by_id(
        self, sources: SourceResource, httpx_mock
    ) -> None:
        """Get a specific connection by ID."""
        httpx_mock.add_response(
            url=f"https://api.getguru.com/api/v1/sources/groups/{CONNECTION_UUID}",
            json=_grouped_connection_json(),
        )
        result = sources.get_connection(CONNECTION_UUID)
        assert isinstance(result, GroupedSourceConnection)
        assert result.id == CONNECTION_UUID
        assert result.name == "Confluence"

    def test_validates_group_id(self, sources: SourceResource) -> None:
        """Empty group_id raises ValidationError."""
        with pytest.raises(ValidationError):
            sources.get_connection("")

    def test_validates_control_chars(self, sources: SourceResource) -> None:
        """Control chars in group_id are rejected."""
        with pytest.raises(ValidationError):
            sources.get_connection("group\x00id")
