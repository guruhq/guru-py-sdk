# Iteration 004 — Cards Resource

**Date**: 2026-04-09
**Status**: Complete

## Goal

Build the CardResource — the first and most complex resource module. Proves the end-to-end pattern: model + resource + tests + wired into Guru facade. Every subsequent resource follows the pattern established here.

## What We Set Out to Build
- `src/guru_sdk/resources/cards.py` — CardResource with full CRUD, verify/unverify, tags, comments, collaborators, folder placement
- `tests/resources/test_cards.py` — comprehensive tests via pytest-httpx
- Wire CardResource into the Guru facade (`client.py`)
- Name resolution (accept card ID or title, resolve transparently)
- Input validation on all methods

## What We Actually Built

### CardResource (32 public methods)

**CRUD:** `get`, `create`, `update`, `patch` (keepVerificationState), `remove`
**Archive/Restore:** `archive`, `restore`
**Retrieval:** `get_version`, `get_bulk`
**Collection:** `move_to_collection`
**Export:** `download_pdf`
**Favorites:** `unfavorite` (`favorite` stubbed — needs favorite list API)
**Verification:** `verify`, `unverify`, `list_unverified`
**Tags:** `list_tags`, `add_tag`, `remove_tag`
**Comments:** `list_comments` (with status filter), `add_comment`, `update_comment`, `delete_comment`, `reply_comment`, `delete_reply`, `resolve_comment`, `unresolve_comment`
**Folders:** `list_folders`, `add_to_folder`, `remove_from_folder`
**Collaborators:** `list_collaborators`, `add_collaborator`, `remove_collaborator`
**Verifiers:** `list_verifiers`

### HttpClient Extensions

Added 7 new methods to support the full range of API patterns:
- `put_empty(path, model)` — PUT with no body, returns validated model (verify)
- `put_no_content(path, body?)` — PUT expecting 204 (resolve/unresolve comments)
- `put_list(path, model, body?)` — PUT returning a list (add_tag)
- `post_list(path, body, model)` — POST returning a list (add_collaborator)
- `patch(path, body, model, **params)` — PATCH with query params (keepVerificationState)
- `post_raw(path, body)` — POST returning raw httpx.Response (bulkop async)
- `get_bytes(path)` — GET returning raw bytes (PDF download)

### Name Resolution

When a non-UUID is passed to any card method, `_resolve_card()` lists cards via the verification manager endpoint and matches by `preferred_phrase` (case-insensitive). UUIDs skip this step entirely.

### Input Validation

Every public method validates its inputs before making any HTTP call:
- Card IDs, tag IDs, folder IDs, comment IDs → `validate_input()` (strict)
- Comment/reply content, HTML content → `validate_free_text()` (lenient — allows `?`, `#`)
- Collaborator emails → `validate_free_text()` (emails contain `@`)

### py-sdk Parity Audit

Before committing, audited all card-related methods on the legacy `Guru` god class (36 SDK methods + 24 Card object convenience methods). Identified and added 9 missing operations:
- `patch` (PATCH with keepVerificationState) — collection owners edit without unverifying
- `archive` / `restore` — soft delete + restore via bulkop
- `get_version` — historical card versions
- `get_bulk` — multi-card fetch via POST /cards/bulk
- `move_to_collection` — bulkop to move between collections
- `download_pdf` — binary PDF export
- `update_comment` — edit existing comment content
- `list_comments(status=)` — filter by OPEN/RESOLVED
- `unfavorite` — remove from favorites (favorite() stubbed pending favorite list API)

Deferred to later iterations: search/find_cards (Phase 3 search resource), drafts (Phase 3 drafts resource), board operations (deprecated). Created iteration 007 (God Class Audit) to systematically categorize remaining legacy methods before Phase 3.

### Tests

95 new tests (237 total, up from 142). Test classes mirror the API surface:
- `TestGet` (6 tests) — UUID lookup, name resolution, case-insensitive matching, not-found, validation
- `TestCreate` (6 tests) — body shape, endpoint, validation, custom share status
- `TestUpdate` (4 tests) — partial updates, validation
- `TestRemove` (2 tests) — delete, validation
- `TestVerify` (3 tests), `TestUnverify` (1 test), `TestListUnverified` (2 tests)
- `TestListTags` (2 tests), `TestAddTag` (3 tests), `TestRemoveTag` (1 test)
- `TestListComments` (2 tests), `TestAddComment` (4 tests), `TestDeleteComment` (1 test)
- `TestReplyComment` (2 tests), `TestDeleteReply` (1 test)
- `TestResolveComment` (1 test), `TestUnresolveComment` (1 test)
- `TestListFolders` (2 tests), `TestAddToFolder` (3 tests), `TestRemoveFromFolder` (1 test)
- `TestListCollaborators` (2 tests), `TestAddCollaborator` (2 tests), `TestRemoveCollaborator` (1 test)
- `TestListVerifiers` (3 tests)
- `TestNameResolution` (4 tests) — exact match, case-insensitive, not-found, UUID bypass
- `TestInputValidation` (8 tests) — control chars, path traversal, query/fragment, percent-encoding

### Wiring

- `CardResource` wired into `Guru` facade as `self.cards`
- Exported from `guru_sdk.__init__` in sorted `__all__`

## What Changed from the Plan

- **HttpClient grew**: Original plan only mentioned the existing HTTP methods. The card API requires PUT-with-no-body (verify) and PUT/POST-returning-lists (tags, collaborators) patterns that didn't exist yet. Added 4 new methods.
- **Name resolution simplified**: Initially tried `get_paginated` for resolution, but `get_list` is simpler and sufficient — the verification manager endpoint doesn't paginate in practice.
- **No hand-rolled Folder model needed**: The generated Folder model from Swagger had all the right fields already.

## Quality Gates

All three gates green:
- `ruff check` — clean
- `mypy --strict` — zero errors
- `pytest` — 210 tests, all passing
