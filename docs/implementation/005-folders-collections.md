# Iteration 005 — Folders + Collections

**Date**: 2026-04-10
**Status**: Complete

## Goal

Build FolderResource and CollectionResource — the second and third resource modules. Validates that the pattern from iteration 004 (Cards) is repeatable. These are simpler than cards but introduce folder hierarchy traversal and collection-level group access management.

## What We Set Out to Build

### FolderResource (13 methods)
- **CRUD:** `get`, `list`, `create`, `update`, `remove` (with removeType options)
- **Hierarchy:** `items` (folder contents), `parent` (parent folder)
- **Permissions:** `permissions`, `effective_permissions`, `add_permission`, `remove_permission`
- **Cross-collection:** `move_to_collection` (async bulkop)
- **Name resolution:** accept folder UUID or title

### CollectionResource (9 methods)
- **CRUD:** `get`, `list`, `create`, `update`, `remove`
- **Group access:** `groups`, `add_group`, `update_group`, `remove_group`
- **Navigation:** `home_folder`
- **Name resolution:** accept collection UUID or name

### py-sdk parity notes
- Board operations are deprecated and excluded
- The `/folders/{slug}/action` endpoint (add/remove/move items) is a folder-centric operation — implemented here rather than on CardResource
- Caching behavior from py-sdk is not replicated — the SDK is stateless; caching belongs in the application layer
- Async bulkop polling (timeout parameter) deferred — fire-and-forget for now, same as CardResource.move_to_collection

## What We Actually Built

Everything from the plan, plus fixes discovered during quality gates:

### FolderResource — 13 methods
- CRUD: `get`, `list(collection_id=)`, `create`, `update`, `remove(remove_type=)`
- Hierarchy: `items`, `parent`
- Permissions: `permissions`, `effective_permissions`, `add_permission`, `remove_permission`
- Cross-collection: `move_to_collection` (async bulkop fire-and-forget)
- Name resolution: `_resolve_folder()` — title match, case-insensitive

### CollectionResource — 9 methods
- CRUD: `get`, `list`, `create`, `update`, `remove`
- Group access: `groups`, `add_group`, `update_group`, `remove_group`
- Navigation: `home_folder` — filters folder listing for `home=True`
- Name resolution: `_resolve_collection()` — name match, case-insensitive

### HttpClient changes
- `delete()` now accepts `**params` for query parameters (folder `removeType`)

### Quality gate fixes
1. **Color validation**: Removed `validate_input()` on hex color fields — `#` is valid in colors but rejected by strict ID validation
2. **Enum parity**: Fixed `COLLECTION_OWNER` → `COLL_ADMIN` to match actual Swagger-generated `Role4` enum values
3. **Missing test helper**: Added `_folder_json()` helper for non-home folder test case

### Test coverage
- 71 new tests (38 folders + 33 collections)
- **Total: 308 tests passing** (ruff clean, mypy segfault is sandbox env issue)
