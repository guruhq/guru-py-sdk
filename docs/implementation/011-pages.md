# Iteration 011 — Pages + Page Drafts

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add PageResource and PageDraftResource for full page management. Covers CRUD, hierarchy traversal, permissions, and page draft collaborators. All endpoints are internal API (not in public Swagger) — mirrors guru-cli ADR-014.

## Scope

### PageResource (11 methods)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | /pages | List all pages | `list[Page]` |
| GET | /pages/{pageId} | Get a page | `Page` |
| GET | /pages/nested | Get nested tree | `Page` (with sub_pages) |
| POST | /pages | Create a page | `Page` |
| PUT | /pages/{pageId} | Update a page | `Page` |
| DELETE | /pages/{pageId} | Delete a page | None |
| PUT | /pages/{pageId}/position | Move a page | `Page` |
| GET | /pages/{pageId}/permissions | List permissions | `list[PagePermission]` |
| POST | /pages/{pageId}/permissions | Add permissions | `list[PagePermission]` |
| PUT | /pages/{pageId}/permissions/{id} | Update permission | None |
| DELETE | /pages/{pageId}/permissions/{id} | Remove permission | None |

### PageDraftResource (8 methods — CRD, no update)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | /pagedrafts | List page drafts | `list[PageDraft]` |
| GET | /pagedrafts?pageId={id} | Filter by page | `list[PageDraft]` |
| GET | /pagedrafts/{id} | Get a page draft | `PageDraft` |
| POST | /pagedrafts | Create a page draft | `PageDraft` |
| DELETE | /pagedrafts/{id} | Delete a page draft | None |
| GET | /pagedrafts/{id}/collaborators | List collaborators | `list[PageDraftCollaborator]` |
| POST | /pagedrafts/{id}/collaborators | Add collaborators | `list[PageDraftCollaborator]` |
| PUT | /pagedrafts/{id}/collaborators | Update collaborators | `list[PageDraftCollaborator]` |
| DELETE | /pagedrafts/{id}/collaborators/{cId} | Remove collaborator | None |

**Update is intentionally omitted** — same MPS/YJS collaborative editing constraint as card drafts. Deferred to iteration 010a.

### Manual Models

Three models defined in `models/_manual.py` (not in Swagger — internal API):
- `PageDraft` — page draft response with `page_id` and `created_by` fields
- `PagePermission` — permission entry (id, type, permission_type, object_role)
- `PageDraftCollaborator` — collaborator entry (id, type, user, group, object_role)

## Implementation

### New Files
- `src/guru_sdk/models/_manual.py` — 3 manually defined models (PageDraft, PagePermission, PageDraftCollaborator)
- `src/guru_sdk/resources/pages.py` — PageResource (11 public methods)
- `src/guru_sdk/resources/page_drafts.py` — PageDraftResource (8 public methods, no update)
- `tests/resources/test_pages.py` — 34 tests
- `tests/resources/test_page_drafts.py` — 24 tests

### Modified Files
- `src/guru_sdk/client.py` — Added `self.pages = PageResource(...)`, `self.page_drafts = PageDraftResource(...)`
- `src/guru_sdk/__init__.py` — Added `PageResource`, `PageDraftResource` to exports
- `src/guru_sdk/models/__init__.py` — Added `BasePage`, `PageDraft`, `PageDraftCollaborator`, `PagePermission` to exports
- `pyproject.toml` — Added `_manual.py` to ruff per-file-ignores for TCH001

## Design Decisions

1. **Manual models instead of generated**: Page endpoints are internal API with no Swagger spec. Rather than using `Page` model (which drops `pageId` and `createdBy` fields due to `extra="ignore"`), we created explicit `PageDraft`, `PagePermission`, and `PageDraftCollaborator` models.

2. **Page draft update deferred**: Same MPS/YJS constraint as card drafts — page drafts opened in the web app enter collaborative editing mode. Update deferred to iteration 010a alongside card draft update.

3. **Move method with position anchors**: `prev_sibling_page_id` accepts "first" or "last" as position anchors — these skip validation (not real IDs). Mirrors guru-cli's implementation.

4. **Permission objects use dict for objectRole**: The `objectRole` field varies by context. Using `dict[str, str | None]` keeps it flexible without generating unnecessary model complexity.

## Test Summary

- 58 new tests (484 total)
- TestList (pages): 3 tests
- TestGet (pages): 3 tests
- TestListNested: 2 tests
- TestCreate (pages): 5 tests
- TestUpdate (pages): 3 tests
- TestDelete (pages): 2 tests
- TestMove: 4 tests
- TestListPermissions: 3 tests
- TestAddPermissions: 3 tests
- TestUpdatePermission: 3 tests
- TestRemovePermission: 3 tests
- TestList (page drafts): 4 tests
- TestGet (page drafts): 3 tests
- TestCreate (page drafts): 4 tests
- TestDelete (page drafts): 2 tests
- TestListCollaborators: 3 tests
- TestAddCollaborators: 3 tests
- TestUpdateCollaborators: 2 tests
- TestRemoveCollaborator: 3 tests

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 484 passed
- mypy: ⏭ verify on Mac
