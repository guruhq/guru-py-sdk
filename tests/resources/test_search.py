"""Tests for guru_sdk.resources.search — SearchResource.

TDD tests covering the search API surface:
- cards() — keyword card search via GET /search/cardmgr
- documents() — keyword document search via POST /search/documents
- documents_semantic() — semantic/NLQ search via GET /search/documents
- sources() — source record search via POST /search/sourcemgr
- Input validation
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest

from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import (
    Card,
    DocumentSearchResponse,
    NLQSearchResponse,
)
from guru_sdk.resources.search import SearchResource

if TYPE_CHECKING:
    from guru_sdk.http import HttpClient

# =============================================================================
# Test Data — realistic API response shapes
# =============================================================================

CARD_UUID = "a1a1a1a1-a1a1-a1a1-a1a1-a1a1a1a1a1a1"
CARD_UUID_2 = "b2b2b2b2-b2b2-b2b2-b2b2-b2b2b2b2b2b2"
COLLECTION_UUID = "c3c3c3c3-c3c3-c3c3-c3c3-c3c3c3c3c3c3"
SOURCE_UUID = "d4d4d4d4-d4d4-d4d4-d4d4-d4d4d4d4d4d4"


def _card_json(card_id: str = CARD_UUID, title: str = "Test Card") -> dict:
    """Build a realistic Card API response dict."""
    return {
        "id": card_id,
        "preferredPhrase": title,
        "content": "<p>Hello</p>",
        "collection": {
            "id": COLLECTION_UUID,
            "name": "Engineering",
            "color": "#4A90D9",
        },
        "owner": {
            "email": "owner@example.com",
            "firstName": "Card",
            "lastName": "Owner",
        },
        "lastModified": "2025-01-15T10:00:00.000+0000",
        "dateCreated": "2025-01-01T08:00:00.000+0000",
        "verificationState": "TRUSTED",
    }


def _document_json(doc_id: str = "doc-1", title: str = "Test Doc") -> dict:
    """Build a realistic Document API response dict."""
    return {
        "id": doc_id,
        "title": title,
        "url": "https://app.getguru.com/card/" + doc_id,
        "documentType": "GURU",
        "content": "<p>Doc content</p>",
    }


def _document_search_response(total: int = 2, docs: list[dict] | None = None) -> dict:
    """Build a DocumentSearchResponse dict."""
    if docs is None:
        docs = [
            _document_json("doc-1", "First Result"),
            _document_json("doc-2", "Second Result"),
        ]
    return {
        "total": total,
        "facets": {
            "collections": [],
            "tags": [],
            "authors": [],
            "sources": [],
        },
        "documents": docs,
    }


def _nlq_search_response(total: int = 2, docs: list[dict] | None = None) -> dict:
    """Build an NLQSearchResponse dict."""
    if docs is None:
        docs = [
            _document_json("nlq-1", "Semantic Result 1"),
            _document_json("nlq-2", "Semantic Result 2"),
        ]
    return {
        "querySpec": {
            "searchTerms": "test query",
            "maxResults": 10,
        },
        "total": total,
        "facets": {
            "collections": [],
            "tags": [],
        },
        "documents": docs,
    }


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture()
def search(http_client: HttpClient) -> SearchResource:
    """SearchResource wired to the mock HttpClient."""
    return SearchResource(http_client)


# =============================================================================
# cards() — GET /search/cardmgr
# =============================================================================


class TestCards:
    """Keyword card search via GET /search/cardmgr."""

    def test_basic_search(self, search: SearchResource, httpx_mock) -> None:
        """Simple keyword search returns list of Card objects."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=onboarding",
            json=[_card_json(CARD_UUID, "Onboarding Guide")],
        )
        results = search.cards("onboarding")
        assert len(results) == 1
        assert isinstance(results[0], Card)
        assert results[0].preferred_phrase == "Onboarding Guide"

    def test_empty_results(self, search: SearchResource, httpx_mock) -> None:
        """Search with no matches returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=nonexistent",
            json=[],
        )
        results = search.cards("nonexistent")
        assert results == []

    def test_multiple_results(self, search: SearchResource, httpx_mock) -> None:
        """Search returning multiple cards."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=test",
            json=[
                _card_json(CARD_UUID, "Test Card 1"),
                _card_json(CARD_UUID_2, "Test Card 2"),
            ],
        )
        results = search.cards("test")
        assert len(results) == 2
        assert results[0].id == CARD_UUID
        assert results[1].id == CARD_UUID_2

    def test_with_max_results(self, search: SearchResource, httpx_mock) -> None:
        """max_results is passed as query param."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=test&maxResults=5",
            json=[_card_json()],
        )
        results = search.cards("test", max_results=5)
        assert len(results) == 1

    def test_with_show_archived(self, search: SearchResource, httpx_mock) -> None:
        """showArchived=true is passed as query param."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=old&showArchived=true",
            json=[_card_json()],
        )
        results = search.cards("old", show_archived=True)
        assert len(results) == 1

    def test_with_query_type(self, search: SearchResource, httpx_mock) -> None:
        """queryType param controls which card types to search."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/cardmgr?q=draft&queryType=draft",
            json=[_card_json()],
        )
        results = search.cards("draft", query_type="draft")
        assert len(results) == 1

    def test_validates_query(self, search: SearchResource) -> None:
        """Empty query string raises ValidationError."""
        with pytest.raises(ValidationError):
            search.cards("")

    def test_validates_control_chars(self, search: SearchResource) -> None:
        """Query with control characters raises ValidationError."""
        with pytest.raises(ValidationError):
            search.cards("test\x00query")


# =============================================================================
# documents() — POST /search/documents
# =============================================================================


class TestDocuments:
    """Keyword document search via POST /search/documents."""

    def test_basic_search(self, search: SearchResource, httpx_mock) -> None:
        """Basic keyword search returns DocumentSearchResponse."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/documents",
            json=_document_search_response(),
        )
        result = search.documents("onboarding")
        assert isinstance(result, DocumentSearchResponse)
        assert result.total == 2
        assert len(result.documents) == 2

    def test_sends_search_terms_in_body(self, search: SearchResource, httpx_mock) -> None:
        """searchTerms is sent in the POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/documents",
            json=_document_search_response(total=1, docs=[_document_json()]),
        )
        search.documents("API reference")
        # Verify the request body
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["searchTerms"] == "API reference"

    def test_with_optional_params(self, search: SearchResource, httpx_mock) -> None:
        """Optional params are included in the POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/documents",
            json=_document_search_response(),
        )
        search.documents(
            "test",
            max_results=10,
            include_content=True,
            collection_ids=[COLLECTION_UUID],
            source_ids=[SOURCE_UUID],
            source_types=["SALESFORCE"],
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["searchTerms"] == "test"
        assert body["maxResults"] == 10
        assert body["includeContent"] is True
        assert body["collectionIds"] == [COLLECTION_UUID]
        assert body["sourceIds"] == [SOURCE_UUID]
        assert body["sourceTypes"] == ["SALESFORCE"]

    def test_omits_none_params(self, search: SearchResource, httpx_mock) -> None:
        """None/default params are not sent in the body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/documents",
            json=_document_search_response(),
        )
        search.documents("test")
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {"searchTerms": "test"}

    def test_validates_search_terms(self, search: SearchResource) -> None:
        """Empty search_terms raises ValidationError."""
        with pytest.raises(ValidationError):
            search.documents("")

    def test_empty_documents_list(self, search: SearchResource, httpx_mock) -> None:
        """Response with no documents returns empty list."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/documents",
            json=_document_search_response(total=0, docs=[]),
        )
        result = search.documents("nope")
        assert result.total == 0
        assert result.documents == []


# =============================================================================
# documents_semantic() — GET /search/documents
# =============================================================================


class TestDocumentsSemantic:
    """Semantic/NLQ search via GET /search/documents."""

    def test_basic_search(self, search: SearchResource, httpx_mock) -> None:
        """Basic semantic search returns NLQSearchResponse."""
        httpx_mock.add_response(
            method="GET",
            json=_nlq_search_response(),
        )
        result = search.documents_semantic("what is onboarding")
        assert isinstance(result, NLQSearchResponse)
        assert result.total == 2
        assert len(result.documents) == 2
        # Verify query params
        request = httpx_mock.get_request()
        assert "searchTerms=what" in str(request.url)

    def test_with_max_results(self, search: SearchResource, httpx_mock) -> None:
        """maxResults is passed as query param."""
        httpx_mock.add_response(
            method="GET",
            json=_nlq_search_response(),
        )
        result = search.documents_semantic("test", max_results=5)
        assert result.total == 2
        request = httpx_mock.get_request()
        assert "maxResults=5" in str(request.url)

    def test_with_agent_id(self, search: SearchResource, httpx_mock) -> None:
        """agentId is passed as query param."""
        agent_id = "e5e5e5e5-e5e5-e5e5-e5e5-e5e5e5e5e5e5"
        httpx_mock.add_response(
            method="GET",
            json=_nlq_search_response(),
        )
        result = search.documents_semantic("test", agent_id=agent_id)
        assert result.total == 2
        request = httpx_mock.get_request()
        assert f"agentId={agent_id}" in str(request.url)

    def test_with_include_content(self, search: SearchResource, httpx_mock) -> None:
        """includeContent is passed as query param."""
        httpx_mock.add_response(
            method="GET",
            json=_nlq_search_response(),
        )
        search.documents_semantic("test", include_content=True)
        request = httpx_mock.get_request()
        assert "includeContent=true" in str(request.url)

    def test_validates_search_terms(self, search: SearchResource) -> None:
        """Empty search_terms raises ValidationError."""
        with pytest.raises(ValidationError):
            search.documents_semantic("")

    def test_query_spec_in_response(self, search: SearchResource, httpx_mock) -> None:
        """NLQSearchResponse includes the resolved querySpec."""
        httpx_mock.add_response(
            method="GET",
            json=_nlq_search_response(),
        )
        result = search.documents_semantic("how do I")
        assert result.query_spec is not None
        assert result.query_spec.search_terms == "test query"


# =============================================================================
# sources() — POST /search/sourcemgr
# =============================================================================


class TestSources:
    """Source record search via POST /search/sourcemgr."""

    def test_basic_search(self, search: SearchResource, httpx_mock) -> None:
        """Basic source search returns DocumentSearchResponse."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/sourcemgr",
            json=_document_search_response(),
        )
        result = search.sources(search_terms="deployment")
        assert isinstance(result, DocumentSearchResponse)
        assert result.total == 2

    def test_sends_body(self, search: SearchResource, httpx_mock) -> None:
        """Search terms and filters are sent in the POST body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/sourcemgr",
            json=_document_search_response(),
        )
        search.sources(
            search_terms="test",
            max_results=20,
            collection_ids=[COLLECTION_UUID],
            source_ids=[SOURCE_UUID],
            source_types=["JIRA"],
        )
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body["searchTerms"] == "test"
        assert body["maxResults"] == 20
        assert body["collectionIds"] == [COLLECTION_UUID]
        assert body["sourceIds"] == [SOURCE_UUID]
        assert body["sourceTypes"] == ["JIRA"]

    def test_no_search_terms(self, search: SearchResource, httpx_mock) -> None:
        """sources() can be called without search_terms (browse mode)."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/sourcemgr",
            json=_document_search_response(),
        )
        result = search.sources(source_ids=[SOURCE_UUID])
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert "searchTerms" not in body
        assert body["sourceIds"] == [SOURCE_UUID]
        assert result.total == 2

    def test_empty_body(self, search: SearchResource, httpx_mock) -> None:
        """sources() with no params sends empty body."""
        httpx_mock.add_response(
            url="https://api.getguru.com/api/v1/search/sourcemgr",
            json=_document_search_response(total=0, docs=[]),
        )
        result = search.sources()
        request = httpx_mock.get_request()
        body = json.loads(request.content)
        assert body == {}
        assert result.total == 0

    def test_validates_search_terms_control_chars(self, search: SearchResource) -> None:
        """Control chars in search_terms are rejected."""
        with pytest.raises(ValidationError):
            search.sources(search_terms="test\x00query")
