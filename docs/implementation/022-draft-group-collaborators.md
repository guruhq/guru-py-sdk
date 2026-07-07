# Iteration 022 — Draft Group Collaborators

**Date**: 2026-07-07
**Status**: Complete
**Story**: sc-156806

## Goal

Extend card draft collaborator management to support user-group collaborators — allowing groups to be added to and removed from card drafts via `DraftResource`, matching the Guru API's `userGroup` collaborator type.

## What We Set Out to Build

- Fix `DraftCollaborator` model to correctly parse the `userGroup` field returned by the card drafts API
- `DraftResource.add_group_collaborators(draft_id, group_ids)` — POST /drafts/{id}/collaborators with `type: "user-group"` body
- `DraftResource.remove_group_collaborator(draft_id, group_id)` — thin alias over `remove_collaborator`
- Tests covering body shape, response parsing, validation, and removal

## What We Actually Built

### Model fix (`src/guru_sdk/models/_manual.py`)

Renamed `DraftCollaborator.group` to `DraftCollaborator.user_group` with alias `userGroup`. This is the core correctness fix: the card drafts API returns `{"userGroup": {...}}` (camelCase, no underscore), but the field was previously named `group` with no alias, so group collaborator objects silently dropped the group identity on parse.

`PageDraftCollaborator.group` is intentionally left unchanged — page draft collaborators use the key `group` (not `userGroup`). This divergence is real API behavior documented in ADR-014.

### New methods (`src/guru_sdk/resources/drafts.py`)

- `add_group_collaborators(draft_id, group_ids)`: validates both inputs, posts
  `{"collaborators": [{"type": "user-group", "userGroup": {"id": gid}} for gid in group_ids]}`,
  returns `list[DraftCollaborator]`
- `remove_group_collaborator(draft_id, group_id)`: delegates to `remove_collaborator(draft_id, group_id)`

### Tests (`tests/resources/test_drafts.py`)

8 new tests added (23 existing → 31 total for the file):

- `TestAddGroupCollaborators`: result parse, correct request-body shape (`type: "user-group"`, `userGroup.id`), draft_id validation, group_ids validation (empty list, blank string in list)
- `TestRemoveGroupCollaborator`: 204 delete, draft_id validation, group_id validation
- Fixture: `group_collaborator_response` with `userGroup` key to verify field aliasing

## Key Architectural Decision: `userGroup` vs `group` Field Names

The `DraftCollaborator` and `PageDraftCollaborator` models now diverge intentionally on their group-identity field:

| Model | Field name | JSON key | Reason |
|---|---|---|---|
| `DraftCollaborator` | `user_group` | `userGroup` | Card drafts API returns `userGroup` |
| `PageDraftCollaborator` | `group` | `group` | Page drafts API returns `group` |

This matches guru-cli's internal schemas exactly. See ADR-014 for the full rationale.

## Breaking Change

`DraftCollaborator.group` has been renamed to `DraftCollaborator.user_group`. Any caller reading `.group` on a card-draft collaborator object must update to `.user_group`. `PageDraftCollaborator.group` is not affected.

## Files Changed

- `src/guru_sdk/models/_manual.py` — `DraftCollaborator.group` → `user_group` (alias `userGroup`)
- `src/guru_sdk/resources/drafts.py` — added `add_group_collaborators`, `remove_group_collaborator`
- `tests/resources/test_drafts.py` — 8 new tests (23 → 31)

## Test Coverage

- `TestAddGroupCollaborators`: result parse, request-body shape, draft_id validation, group_ids validation.
- `TestRemoveGroupCollaborator`: 204 delete, draft_id validation, group_id validation.
- All 706 tests pass; `ruff` and `mypy --strict` clean.
