# Iteration 008 — Search

**Status**: Complete
**Date**: 2026-04-10

## Goal

Add SearchResource to cover keyword and semantic search across cards, sources, and documents. Covers py-sdk's `find_card`, `find_cards`, `get_visible_cards` and adds document/source search capabilities.

## Scope

### Endpoints (Public Swagger)

| Method | Endpoint | Description | Response Model |
|--------|----------|-------------|----------------|
| GET | /search/cardmgr | Keyword card search (paginated) | `list[Card]` |
| POST | /search/documents | Keyword search across cards + sources | `DocumentSearchResponse` |
| GET | /search/documents | Semantic/NLQ search across cards + sources | `NLQSearchResponse` |
| POST | /search/sourcemgr | Source record search | `DocumentSearchResponse` |

### Public API (4 methods)

- `cards(query, *, max_results, show_archived, query_type)` → `list[Card]`
- `documents(search_terms, *, max_results, include_content, collection_ids, source_ids, source_types)` → `DocumentSearchResponse`
- `documents_semantic(search_terms, *, max_results, include_content, agent_id)` → `NLQSearchResponse`
- `sources(*, search_terms, max_results, collection_ids, source_ids, source_types)` → `DocumentSearchResponse`

### Not included (deferred)

- POST /search/cardmgr (advanced card search with Expression queries) — can be added later
- GET /search/query (legacy alias of cardmgr) — redundant
- GET /search/sourcemgr/filters/sources — belongs in SourceResource (iteration 009)

## Implementation

### New Files
- `src/guru_sdk/resources/search.py` — SearchResource (4 public methods + 1 private helper)
- `tests/resources/test_search.py` — 25 tests

### Modified Files
- `src/guru_sdk/client.py` — Added `self.search = SearchResource(self._http)`
- `src/guru_sdk/__init__.py` — Added `SearchResource` to exports
- `src/guru_sdk/models/__init__.py` — Added `Document`, `DocumentSearchResponse`, `NLQSearchResponse`, `SearchFacets` to exports
- `README.md` — Added Search section with code examples
- `docs/implementation/backlog.md` — Moved 008 to Completed

### Design Decisions

1. **Public endpoints only**: guru-cli uses non-public endpoints (`/search/cards`, `/search/semantic/cards`, `/search/semantic/documents`). The py-sdk sticks to the public Swagger spec for stability.

2. **GET vs POST**: Card search uses GET (simple query params, paginated via Link headers). Document keyword search uses POST (SearchQuerySpec body). Semantic search uses GET (query params — the NLQ endpoint).

3. **Empty string validation**: Added explicit empty-string checks in search methods. `validate_free_text()` only checks control chars — empty search queries are semantically invalid but technically pass that check.

4. **Shared body builder**: `_build_search_body()` static method shared between `documents()` and `sources()` to DRY the SearchQuerySpec construction.

5. **sources() all-optional**: Unlike `cards()` and `documents()`, `sources()` accepts all-optional params for browse mode (no search terms required).

## Test Summary

- 25 new tests (396 total)
- TestCards: 8 tests (basic, empty, multiple, max_results, show_archived, query_type, validation ×2)
- TestDocuments: 6 tests (basic, body verification, optional params, omits none, validation, empty docs)
- TestDocumentsSemantic: 6 tests (basic, max_results, agent_id, include_content, validation, query_spec)
- TestSources: 5 tests (basic, body verification, no search_terms, empty body, validation)

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 396 passed
- mypy: ⏭ segfaults in sandbox (known env limitation, passes on Mac)
