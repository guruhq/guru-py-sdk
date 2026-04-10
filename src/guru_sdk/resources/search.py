"""Search resource — keyword and semantic search across cards, sources, and documents.

Covers five public Guru API search endpoints:
- GET  /search/cardmgr   — keyword card search (query param, paginated)
- POST /search/cardmgr   — advanced card search (JSON body, paginated)
- GET  /search/documents  — semantic/NLQ search across cards + sources
- POST /search/documents  — keyword search across cards + sources
- POST /search/sourcemgr  — search source records

This resource exposes four public methods mapping to the most useful patterns.
The POST /search/cardmgr (advanced card search with Expression queries) can be
added later if needed.

API surface mirrors guru-cli's SearchResource with adjustments for the public
Swagger spec (guru-cli uses some non-public endpoints like /search/cards and
/search/semantic/cards that are not available here).
"""

from __future__ import annotations

from typing import Any

from guru_sdk._compat import validate_free_text
from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import (
    Card,
    DocumentSearchResponse,
    NLQSearchResponse,
)
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — SearchResource
# =============================================================================


class SearchResource(BaseResource):
    """Guru Search — keyword and semantic search across cards and sources.

    Methods:
        cards()              — keyword card search (GET /search/cardmgr)
        documents()          — keyword document search (POST /search/documents)
        documents_semantic() — semantic/NLQ search (GET /search/documents)
        sources()            — source record search (POST /search/sourcemgr)
    """

    # -------------------------------------------------------------------------
    # Card search — GET /search/cardmgr
    # -------------------------------------------------------------------------

    def cards(
        self,
        query: str,
        *,
        max_results: int | None = None,
        show_archived: bool = False,
        query_type: str | None = None,
    ) -> list[Card]:
        """Keyword search for cards.

        Args:
            query: Search query string.
            max_results: Maximum number of results (API default 50).
            show_archived: Include archived cards in results.
            query_type: Card type filter — "cards", "archived", "draft",
                        "legacy", "search_cards".
        """
        if not query.strip():
            raise ValidationError("query must not be empty")
        validate_free_text(query, "query")
        # Build query params — only include non-default values
        params: dict[str, Any] = {"q": query}
        if max_results is not None:
            params["maxResults"] = max_results
        if show_archived:
            params["showArchived"] = "true"
        if query_type is not None:
            params["queryType"] = query_type
        return self._http.get_paginated("/search/cardmgr", Card, **params)

    # -------------------------------------------------------------------------
    # Document search — POST /search/documents (keyword)
    # -------------------------------------------------------------------------

    def documents(
        self,
        search_terms: str,
        *,
        max_results: int | None = None,
        include_content: bool = False,
        collection_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> DocumentSearchResponse:
        """Keyword search across Guru cards and connected sources.

        Args:
            search_terms: Search query string.
            max_results: Maximum number of results.
            include_content: Include full card content in results.
            collection_ids: Filter by collection UUIDs.
            source_ids: Filter by source UUIDs.
            source_types: Filter by source types (e.g. "SALESFORCE").
        """
        if not search_terms.strip():
            raise ValidationError("search_terms must not be empty")
        validate_free_text(search_terms, "search_terms")
        body = self._build_search_body(
            search_terms=search_terms,
            max_results=max_results,
            include_content=include_content,
            collection_ids=collection_ids,
            source_ids=source_ids,
            source_types=source_types,
        )
        return self._http.post("/search/documents", body, DocumentSearchResponse)

    # -------------------------------------------------------------------------
    # Document search — GET /search/documents (semantic / NLQ)
    # -------------------------------------------------------------------------

    def documents_semantic(
        self,
        search_terms: str,
        *,
        max_results: int | None = None,
        include_content: bool = False,
        agent_id: str | None = None,
    ) -> NLQSearchResponse:
        """Semantic (natural language) search across cards and sources.

        Uses the NLQ endpoint which interprets the query semantically rather
        than doing exact keyword matching.

        Args:
            search_terms: Natural language search query.
            max_results: Maximum number of results.
            include_content: Include full card content in results.
            agent_id: Scope search to a specific Knowledge Agent.
        """
        if not search_terms.strip():
            raise ValidationError("search_terms must not be empty")
        validate_free_text(search_terms, "search_terms")
        params: dict[str, Any] = {"searchTerms": search_terms}
        if max_results is not None:
            params["maxResults"] = max_results
        if include_content:
            params["includeContent"] = "true"
        if agent_id is not None:
            params["agentId"] = agent_id
        return self._http.get("/search/documents", NLQSearchResponse, **params)

    # -------------------------------------------------------------------------
    # Source search — POST /search/sourcemgr
    # -------------------------------------------------------------------------

    def sources(
        self,
        *,
        search_terms: str | None = None,
        max_results: int | None = None,
        collection_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> DocumentSearchResponse:
        """Search source records.

        All params are optional — call with no args to browse all sources.

        Args:
            search_terms: Search query string.
            max_results: Maximum number of results.
            collection_ids: Filter by collection UUIDs.
            source_ids: Filter by source UUIDs.
            source_types: Filter by source types (e.g. "JIRA").
        """
        if search_terms is not None:
            validate_free_text(search_terms, "search_terms")
        body = self._build_search_body(
            search_terms=search_terms,
            max_results=max_results,
            collection_ids=collection_ids,
            source_ids=source_ids,
            source_types=source_types,
        )
        return self._http.post("/search/sourcemgr", body, DocumentSearchResponse)

    # -------------------------------------------------------------------------
    # Private — build SearchQuerySpec body from keyword arguments
    # -------------------------------------------------------------------------

    @staticmethod
    def _build_search_body(
        *,
        search_terms: str | None = None,
        max_results: int | None = None,
        include_content: bool = False,
        collection_ids: list[str] | None = None,
        source_ids: list[str] | None = None,
        source_types: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build the SearchQuerySpec JSON body, omitting None/default values."""
        body: dict[str, Any] = {}
        if search_terms is not None:
            body["searchTerms"] = search_terms
        if max_results is not None:
            body["maxResults"] = max_results
        if include_content:
            body["includeContent"] = True
        if collection_ids:
            body["collectionIds"] = collection_ids
        if source_ids:
            body["sourceIds"] = source_ids
        if source_types:
            body["sourceTypes"] = source_types
        return body
