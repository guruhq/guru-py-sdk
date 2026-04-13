# Iteration 015 — Publisher (Folder-Based Content Sync)

**Status**: Complete
**Date**: 2026-04-13

## Goal

Port the legacy `PublisherFolders` class from `py-sdk/guru/publish_folders.py` to `contrib/publisher.py`. This is an abstract base class framework for syncing Guru collection content to external systems. Users subclass it and implement hooks for their target system.

## Architecture

The Publisher walks a Guru collection's folder hierarchy, compares each item against a local metadata file (JSON) to detect changes, and calls abstract methods that subclasses implement to sync to the external system.

### Sync Flow
1. `publish_collection(collection_id)` — entry point
2. Gets the home folder, then recursively walks folders/cards
3. For each item: check metadata → detect changes → call create/update hook
4. `process_deletions()` — finds items in metadata that weren't visited → calls delete hooks

### Key Concepts
- **Metadata file**: JSON dict mapping `guru_id → {external_id, type, last_updated, folders, tags}`. Persisted to disk between runs.
- **CardChanges**: Dataclass tracking what changed (content, folder assignments, tags).
- **Abstract hooks**: Subclasses implement `create_external_card`, `update_external_card`, `delete_external_card` (required) and folder/collection equivalents (optional).
- **Link rewriting**: Converts cross-card Guru links to external URLs via `get_external_url` hook.

## Scope

### Classes
- `CardChanges` — frozen dataclass with content_changed, folders_added/removed, tags_added/removed
- `PublisherFolders` — abstract base class with ~15 methods

### PublisherFolders Public Methods
| Method | Description |
|--------|-------------|
| `publish_collection(collection_id)` | Walk entire collection, sync all items |
| `publish_folder(folder_id, collection_id)` | Sync a single folder and its contents |
| `publish_card(card, collection, folder)` | Sync a single card |
| `process_deletions()` | Delete items from external system that were removed from Guru |
| `get_card_changes(card)` | Compute what changed since last publish |
| `get_external_id(guru_id)` | Look up external ID from metadata |
| `save_metadata()` | Persist metadata to disk |

### Abstract Hooks (subclasses implement)
| Hook | Required | Description |
|------|----------|-------------|
| `create_external_card` | Yes | Create card in external system, return external_id |
| `update_external_card` | Yes | Update card in external system |
| `delete_external_card` | Yes | Delete card from external system |
| `get_external_url` | Yes | Convert external_id to URL (for link rewriting) |
| `create_external_folder` | No | Create folder in external system |
| `update_external_folder` | No | Update folder in external system |
| `delete_external_folder` | No | Delete folder from external system |
| `create_external_collection` | No | Create collection in external system |
| `update_external_collection` | No | Update collection in external system |
| `delete_external_collection` | No | Delete collection from external system |
| `find_external_card` | No | Find pre-existing external card |
| `find_external_folder` | No | Find pre-existing external folder |
| `find_external_collection` | No | Find pre-existing external collection |

## Design Decisions

1. **Modernized with dataclasses**: `CardChanges` is a frozen dataclass instead of a plain class.
2. **pathlib for file I/O**: Metadata uses `pathlib.Path` instead of the legacy `read_file/write_file` utilities.
3. **No BeautifulSoup dependency**: Link rewriting uses stdlib `html.parser` (consistent with `contrib/content.py`).
4. **Explicit save_metadata()**: Instead of auto-saving on every change (legacy behavior), callers explicitly save. More predictable for dry-run mode.
5. **Type annotations throughout**: Full typing for all methods, parameters, and return values.
6. **Uses new SDK resource methods**: `g.collections.home_folder()`, `g.folders.items()`, `g.cards.get()`, etc.
7. **Card data fetched per-item**: Since our Pydantic models don't have pre-loaded `.folders`/`.tags` like the legacy SDK, the publisher calls `g.cards.list_folders()` and `g.cards.list_tags()` when computing changes.

## Implementation

### New Files
- `src/guru_sdk/contrib/publisher.py` — CardChanges + PublisherFolders
- `tests/contrib/test_publisher.py` — tests

### Modified Files
- `src/guru_sdk/contrib/__init__.py` — add publisher exports

## Test Summary

25 new tests in `tests/contrib/test_publisher.py`:
- **CardChanges** (5): construction, needs_publishing logic, no-changes case, frozen immutability
- **Metadata** (7): load from disk, save to disk, missing file creates empty, get/set external ID, visited tracking
- **publish_card** (5): new card (create hook), existing unchanged (skip), existing changed (update hook), content changes, folder/tag changes
- **publish_folder** (3): recursive walk, folder create hook, nested folders
- **publish_collection** (1): end-to-end walk from collection → home folder → folders → cards
- **process_deletions** (4): delete unvisited cards, delete unvisited folders, no deletions when all visited, mixed types

Total: 611 tests (586 → 611, +25)

## Quality Gates

```
ruff check   ✅ (zero errors)
mypy         ⏭ (segfaults in sandbox — verified on Mac)
pytest       ✅ 611 passed in 8.45s
```
