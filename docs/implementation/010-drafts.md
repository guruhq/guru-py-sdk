# Iteration 010 — Drafts

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add DraftResource for CRD operations on draft cards. Covers py-sdk's `get_drafts`, `create_draft`, `delete_draft`.

## Scope

### CRD Only — No Update

Update is intentionally omitted. When a draft is opened in the Guru web app, it enters collaborative editing mode controlled by MPS and YJS (real-time collaborative editing). Updates from outside that experience must "politely fail" if the draft is actively being edited. A draft that exists but hasn't been opened for editing *could* be updated, but the architecture to detect and handle the editing state doesn't exist yet.

Future iteration 010a will add: update (with politely-fail semantics), publishing context, collaborator management.

### Endpoints

| Method | Endpoint | Description | Response | Swagger |
|--------|----------|-------------|----------|---------|
| GET | /drafts | List all drafts | `list[DraftCard]` | No* |
| GET | /drafts?cardId={id} | List drafts for a card | `list[DraftCard]` | No* |
| GET | /drafts/{draftId} | Get a draft | `DraftCard` | No* |
| POST | /drafts | Create a draft | `DraftCard` | No* |
| DELETE | /drafts/{draftId} | Delete a draft | None | No* |

*Not in public Swagger but used by guru-cli. Works in practice.

### Public API (4 methods)

- `list(*, card_id=None)` → `list[DraftCard]`
- `get(draft_id)` → `DraftCard`
- `create(*, title, content=None, json_content=None, card_id=None)` → `DraftCard`
- `delete(draft_id)` → None

## Implementation

### New Files
- `src/guru_sdk/resources/drafts.py` — DraftResource (4 public methods)
- `tests/resources/test_drafts.py` — 14 tests

### Modified Files
- `src/guru_sdk/client.py` — Added `self.drafts = DraftResource(self._http)`
- `src/guru_sdk/__init__.py` — Added `DraftResource` to exports

## Test Summary

- 14 new tests (426 total)
- TestList: 4 tests (all, empty, by card_id, nested fields)
- TestGet: 3 tests (by ID, empty validation, control chars)
- TestCreate: 5 tests (minimal, body check, all fields, omits none, title validation)
- TestDelete: 2 tests (success, empty validation)

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 426 passed
- mypy: ⏭ verify on Mac
