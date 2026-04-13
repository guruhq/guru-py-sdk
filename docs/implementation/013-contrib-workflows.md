# Iteration 013 — Contrib: Workflows

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add convenience workflows that compose multiple resource calls into higher-level operations. These live in `contrib/workflows.py` — outside the core resource layer. Each function takes a `Guru` client as its first argument.

## Scope

### Functions (6)

| Function | What It Does | Underlying Calls |
|----------|-------------|-----------------|
| `move_card_between_folders` | Remove card from source folder, add to target | `cards.remove_from_folder` + `cards.add_to_folder` |
| `batch_add_users_to_group` | Add many emails to one group in batches of 100, retry failures | `groups.add_members` in chunks |
| `add_user_to_groups` | Add one email to multiple groups | `groups.add_members` per group |
| `remove_user_from_groups` | Remove one email from multiple groups | `groups.remove_member` per group |
| `make_collection_with_setup` | Create collection + add group access | `collections.create` + `collections.add_group` |
| `add_tag_with_auto_create` | Add tag to card, creating tag if not found | `tags.get_tag` (try) + `tags.create_tag` (if missing) + `cards.add_tag` |

### Dropped from Backlog

- **`move_folder_to_folder`** — uses internal `/folders/{slug}/action` endpoint with `item_id` and `legacyType: "BOARD"` fields not in the public swagger spec. Not a public API operation.
- **`set_item_save_folder`** — same internal action endpoint. Not a public API operation.

## Design Decisions

1. **Free functions, not methods**: Workflows are `def func(g: Guru, ...)` — not methods on the Guru class. Keeps the core lean, contrib is opt-in.
2. **Return results dict for batch ops**: `batch_add_users_to_group`, `add_user_to_groups`, `remove_user_from_groups` return `dict[str, bool]` mapping email/group → success.
3. **No caching or state**: Workflows are stateless — they call resource methods and return results. No internal caching.
4. **Validation at resource layer**: Workflows rely on the existing resource-layer validation. No duplicate validation.
5. **Error semantics**: Individual failures in batch operations are captured in the result dict, not raised. Total failures (e.g., group not found) raise normally.

## Implementation

### New Files
- `src/guru_sdk/contrib/workflows.py` — 6 public functions
- `tests/contrib/test_workflows.py` — tests

### Modified Files
- `src/guru_sdk/contrib/__init__.py` — re-export all 6 workflow functions

## Test Summary

- 23 new tests (558 total)
- move_card_between_folders: 3 tests (happy path, remove failure propagates, accepts names)
- batch_add_users_to_group: 5 tests (small batch, splits at 100, retry with smaller batch, empty list, all retries exhausted)
- add_user_to_groups: 4 tests (happy path, partial failure, empty groups, single group)
- remove_user_from_groups: 3 tests (happy path, partial failure, empty groups)
- make_collection_with_setup: 4 tests (happy path, optional fields, create failure propagates, no group_id skips add_group)
- add_tag_with_auto_create: 4 tests (tag exists, tag not found creates, creation failure propagates, returns tag object)

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 558 passed
- mypy: ⏭ verify on Mac (segfaults in sandbox — known mypy 1.20.0 issue; type annotations verified manually, null checks added for `str | None` fields)
