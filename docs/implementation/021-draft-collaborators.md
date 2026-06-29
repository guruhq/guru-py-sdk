# Iteration 021 — Draft Collaborators

**Date**: 2026-06-29
**Status**: Complete

## Goal

Add collaborator management to `DraftResource` — list, add, and remove collaborators on card drafts, matching guru-cli's `DraftResource` API.

## What We Set Out to Build

- `DraftCollaborator` Pydantic model in `_manual.py` (`id`, `type`, `user`, `group`, `date_created`)
- `DraftResource.list_collaborators(draft_id)` — GET /drafts/{id}/collaborators
- `DraftResource.add_collaborators(draft_id, collaborators)` — POST /drafts/{id}/collaborators
- `DraftResource.remove_collaborator(draft_id, collaborator_id)` — DELETE /drafts/{id}/collaborators/{id}
- Tests for all three methods (mirrors page_drafts collaborator test pattern)

## What We Actually Built

- `DraftCollaborator` model in `src/guru_sdk/models/_manual.py` — fields `id`, `type`,
  `user` (`User`), `group` (dict), `date_created` (alias `dateCreated`). Re-exported
  from `models/__init__.py`.
- Three methods on `DraftResource` (`src/guru_sdk/resources/drafts.py`):
  - `list_collaborators(draft_id)` → `GET /drafts/{id}/collaborators` (via `get_list`)
  - `add_collaborators(draft_id, collaborators)` → `POST /drafts/{id}/collaborators`
    wrapping the body as `{"collaborators": [...]}` (via `post_list`)
  - `remove_collaborator(draft_id, collaborator_id)` → `DELETE /drafts/{id}/collaborators/{cId}`
- 9 new tests in `tests/resources/test_drafts.py` (689 → 698 total).

## What Changed From Plan

- **No `update_collaborators`.** guru-cli's `DraftResource` has only list/add/remove for
  collaborators (unlike `PageDraftResource`, which also has `updateCollaborators`). We
  matched the CLI's card-draft surface exactly rather than the page-draft surface.
- **`DraftCollaborator` shape differs from `PageDraftCollaborator`.** Card draft
  collaborators carry `dateCreated` and have no `objectRole`; page draft collaborators
  have `objectRole` and no `dateCreated`. Modeled per guru-cli's distinct schemas.
- `add_collaborators` takes raw collaborator dicts (matching `page_drafts` SDK pattern),
  not a list of email strings (the CLI's convenience signature). This keeps the SDK's
  two draft resources consistent with each other.

## Test Coverage

- `TestListCollaborators`: multi-result parse, empty list, draft_id validation.
- `TestAddCollaborators`: result parse, request-body wrapping assertion, draft_id validation.
- `TestRemoveCollaborator`: 204 delete, draft_id validation, collaborator_id validation.
- All 698 tests pass; `ruff` and `mypy --strict` clean.
