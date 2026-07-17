# Iteration 025 — Bulk Card Comments

**Date**: 2026-07-17
**Status**: Complete
**Ticket**: sc-157622 — Add bulk card comment retrieval to guru-py-sdk

## Goal

Let callers retrieve card comment threads team-wide (across all accessible
cards) in one paginated call, instead of having to enumerate cards and call
the existing per-card comment endpoints one at a time.

## What We Set Out to Build

- **US-001** (already committed as `7e8e442`): Refresh the vendored
  `swagger/swagger.json` from the live spec and regenerate
  `src/guru_sdk/models/_generated.py`, picking up two new models —
  `CardCommentResult` (flat comment shape with a nested `card` reference) and
  `CardReference` (lightweight id/title/slug) — and export both from
  `src/guru_sdk/models/__init__.py`.
- **US-002** (this story): Add `CardResource.bulk_get_comments()`, consuming
  the team-wide `GET /api/v1/comments` endpoint (not nested under
  `/cards/{cardId}/`, unlike the sibling comment methods). Supports optional
  `status` / `created_after` / `created_before` query-param filters and walks
  `Link`-header pagination via the existing `HttpClient.get_paginated()`.
  TDD: tests first in `tests/resources/test_cards.py`, then the implementation.

## What We Actually Built

- **US-001** (prior commit `7e8e442`): `swagger/swagger.json` refreshed from
  the live public spec; `src/guru_sdk/models/_generated.py` regenerated,
  adding `CardCommentResult` and `CardReference`, both exported from
  `src/guru_sdk/models/__init__.py`.
- **US-002 tests first**: Added `_card_comment_result_json()` fixture helper
  and `TestBulkGetComments` (5 tests) to
  `tests/resources/test_cards.py`, covering: all three query-param filters
  sent correctly (`status`, `createdAfter`, `createdBefore`); no filters →
  no query params; request path is `/api/v1/comments` (not nested under a
  card); response deserializes into `CardCommentResult` with comment fields
  flat at the top level and the card identity nested under `.card` as a
  `CardReference`; two-page pagination via `Link: rel="next"` headers
  aggregates into one list. Ran with `-k BulkGetComments` first and confirmed
  all 5 failed with `AttributeError: 'CardResource' object has no attribute
  'bulk_get_comments'` before writing any implementation.
- **US-002 implementation**: `CardResource.bulk_get_comments()` in
  `src/guru_sdk/resources/cards.py`, placed directly after `list_comments()`.
  Takes `status` / `created_after` / `created_before` / `max_pages` — all
  keyword-only, all optional — validates each provided value with the strict
  `validate_input()` (matching `list_comments`'s status validation, not the
  lenient `validate_free_text()` used for comment bodies), builds the
  camelCase query-param dict, and delegates entirely to the existing
  `HttpClient.get_paginated("/comments", CardCommentResult, max_pages=...,
  **params)` — no new HTTP-layer code needed. Unlike every sibling comment
  method, it takes no `card_id` and never calls `self._resolve_card()`,
  since `/comments` is a team-wide endpoint.
- Added `CardCommentResult` to the `guru_sdk.models` import block in
  `cards.py`. `Any` was already imported.

## What Changed From Plan

- None. The ticket's plan (US-001 model regen, then US-002 add
  `bulk_get_comments` on top of the already-existing `get_paginated`) matched
  what shipped exactly — no API surface, validation, or pagination
  deviations.

## Test Coverage

- 5 new tests in `TestBulkGetComments`
  (`tests/resources/test_cards.py`): query-param filters, no-filter call,
  path assertion, deserialization (flat comment + nested `CardReference`),
  two-page `Link`-header pagination aggregation.
- Full suite: 706 → 711 tests, all passing.
- `uv run ruff check src tests` and `uv run mypy src/guru_sdk/ --strict`:
  both clean.
