# Iteration 026 — Bulk Comment Active Filters

**Date**: 2026-07-30
**Status**: Complete
**Ticket**: sc-158926 — Rename bulk comment filter kwargs to match renamed server query params

## Goal

Rename the misleading `created_after`/`created_before` kwargs on
`CardResource.bulk_get_comments()` to `active_after`/`active_before`, matching
guru-server's renamed `activeAfter`/`activeBefore` query params on the
team-wide `GET /comments` endpoint. The old kwarg names were sent on the wire
as `createdAfter`/`createdBefore`, query params the server no longer
recognizes — since the endpoint silently ignores unknown query params, the
filters silently no-op instead of raising an error.

## What We Set Out to Build

- **US-001** (already committed, separate commit): Full ADR-008 spec refresh
  — re-vendor `swagger/swagger.json` from the live public spec and regenerate
  `src/guru_sdk/models/_generated.py`. Confirmed the refreshed spec renamed
  the `/comments` endpoint's query params from `createdAfter`/`createdBefore`
  to `activeAfter`/`activeBefore`, and confirmed `CardCommentResult` /
  `CardReference` / `CardComment` field sets were unaffected by the refresh —
  this story is a pure rename with no model-shape concerns.
- **US-002** (this story): Rename `bulk_get_comments()`'s `created_after` /
  `created_before` keyword-only params to `active_after` / `active_before`,
  and the query params they populate from `createdAfter`/`createdBefore` to
  `activeAfter`/`activeBefore`. TDD: rename the tests first in
  `tests/resources/test_cards.py`, confirm they fail against the
  not-yet-renamed source, then rename the source.

## What We Actually Built

- **Tests first**: In `tests/resources/test_cards.py`,
  `class TestBulkGetComments`, renamed kwargs and assertions in three tests —
  `test_sends_all_filters_as_query_params`, `test_accepts_full_iso_8601_timestamps`,
  `test_rejects_pre_encoded_iso_8601_timestamp` — from `created_after`/
  `created_before` to `active_after`/`active_before`, and their `createdAfter=`/
  `createdBefore=` URL/param assertions to `activeAfter=`/`activeBefore=`. Ran
  `-k BulkGetComments` and confirmed the three renamed tests failed with
  `TypeError: CardResource.bulk_get_comments() got an unexpected keyword
  argument 'active_after'` against the not-yet-renamed source, while the
  other six tests in the class (no-filter call, path assertion,
  deserialization, pagination) passed unchanged — confirming the tests were
  exercising the right thing before touching source.
- **Source rename**: In `src/guru_sdk/resources/cards.py`,
  `bulk_get_comments()` — renamed the two keyword-only parameters
  `created_after`/`created_before` to `active_after`/`active_before`; updated
  the docstring's parameter label to `active_after / active_before:` (kept
  the existing description "ISO-8601 bounds on the thread's most-recent
  activity (inclusive)" verbatim — it already correctly described server
  behavior, only the label was wrong); updated the `validate_input()` calls
  to reference `active_after`/`active_before` (both the variable and the
  string label); updated `params["createdAfter"]`/`params["createdBefore"]`
  to `params["activeAfter"]`/`params["activeBefore"]`.
- No other files needed changes: the keyword-only signature (`*`) means there
  are no positional callers, and `HttpClient.get_paginated()` passes
  `**params` through untouched regardless of key names.

## What Changed From Plan

- The rename itself landed exactly as scoped — no model-shape concerns
  (confirmed by US-001), no new HTTP-layer code.
- **US-003 (added during review): pin the anonymous numbered enums.** Review
  found that US-001's refresh renumbered 18 surviving `Op*`/`Type*` names onto
  different member sets. No code change was required — `Type8`, the only such
  name referenced outside `_generated.py`, was unchanged — but the absence of
  any test asserting that made the safety accidental. Added a pin table and a
  self-enforcing coverage test so a future refresh cannot repeat the risk
  silently. See the 026 learnings record for the full analysis.

## Test Coverage

- 3 renamed tests in `TestBulkGetComments`
  (`tests/resources/test_cards.py`): filter query-param assertions,
  full-ISO-8601-timestamp handling, pre-encoded-timestamp rejection. All 9
  tests in the class pass (the 3 renamed plus 6 unchanged siblings).
- 2 new tests in `TestPinnedAnonymousEnums`
  (`tests/models/test_generated.py`): `test_pinned_enum_members_unchanged`
  pins `Type8` to `card`/`folder` (consumed by name in `contrib/publisher.py`
  and `contrib/workflows.py`), and
  `test_every_referenced_anonymous_enum_is_pinned` scans `src/guru_sdk/` for
  by-name references to numbered enums and fails on any that lack a pin.
  Both were mutation-verified: emptying the pin table, corrupting the expected
  members, and renaming the pinned key each fail with a distinct message.
- Full suite: 721 tests, all passing (719 after US-002, plus the 2 pins).
- `uv run ruff check src tests`, `uv run ruff format --check src tests`, and
  `uv run mypy src/guru_sdk/ --strict`: all clean.
