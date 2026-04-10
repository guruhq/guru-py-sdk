# Iteration 006 — Groups + Members + Tags

**Date**: 2026-04-10
**Status**: Complete

## Goal

Build GroupResource, MemberResource, and TagResource — completing Phase 2 (core resources). These round out the fundamental Guru entities that users interact with most frequently.

## What We Set Out to Build

### GroupResource (9 methods)
- **CRUD:** `get`, `list`, `create`, `update`, `remove`
- **Member management:** `members` (paginated), `add_members`, `remove_member`
- **Collection access:** `collections` — list collections a group has access to
- **Name resolution:** accept group UUID or name

### MemberResource (4 methods)
- **Read:** `list` (with search), `get` (by email)
- **Write:** `invite` (with type and optional message), `remove`

### TagResource (7 methods + team ID resolution)
- **Categories:** `list_categories`, `create_category`, `update_category`, `delete_category`
- **Tags:** `get_tag`, `create_tag`, `update_tag`
- **Tag name resolution:** search all categories for matching tag name
- **Team ID resolution:** `/whoami` → cached team ID (all tag endpoints need it)

## What We Actually Built

Everything from the plan. Key implementation details:

### GroupResource — 9 methods
- CRUD + member management + collection access
- `members()` uses `get_paginated` for Link-header pagination
- `add_members()` sends `[{"id": email}, ...]` body format per API spec
- `remove_member()` percent-encodes email in URL path (`@ → %40`)
- Name resolution via `_resolve_group()` — list + case-insensitive name match

### MemberResource — 4 methods
- `list(search=)` uses `get_paginated` with initial query params
- `get()` and `remove()` percent-encode email in URL path
- `invite()` supports `member_type` (CORE/LIGHT) and optional custom message
- Uses `validate_free_text()` for search and message fields (natural language)

### TagResource — 7 methods + team ID cache
- All endpoints require team ID — resolved once via `/whoami` using `WhoAmI` model
- Team ID cached at instance level (not class level) so each `Guru` client is independent
- Tag name resolution searches all categories' nested tag lists
- Uses `WhoAmI` model (not `User`) since `/whoami` returns a different schema

### HttpClient changes
- `get_paginated()` now accepts `**params` for initial query parameters (used by member search)

### Quality gate fixes
1. **Invalid test UUIDs**: Group tests used `gggggggg-...` which aren't valid hex — `is_uuid()` correctly rejected them, routing through name resolution instead of direct lookup. Fixed to use valid hex UUIDs (`a0a0a0a0-...`).

### Test coverage
- 63 new tests (27 groups + 13 members + 23 tags)
- **Total: 371 tests passing** (ruff clean, mypy segfault is sandbox env issue)

## py-sdk Parity Notes

### Covered
- Group CRUD, member add/remove, collection listing
- Member list with search, get by email, invite, remove
- Tag CRUD, category CRUD, tag resolution by name

### Deferred
- `add_users_to_group` batch with retry logic — belongs in contrib (convenience workflow)
- `add_user_to_groups` (plural groups) — convenience wrapper, contrib
- `upgrade_light_user` / `downgrade_core_user` — uncommon operations, can add later
- `delete_tag` / `merge_tags` via bulk operations — needs bulk op infrastructure
- Board group sharing — boards are deprecated
