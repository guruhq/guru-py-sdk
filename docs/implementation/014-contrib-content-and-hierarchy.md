# Iteration 014 — Contrib: Content Utilities + Folder Hierarchy

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add content utilities (pure HTML functions) and a folder hierarchy dump workflow. Content utilities are pure functions that operate on HTML strings — no API calls. The hierarchy dump is a workflow that recursively walks a collection's folder tree and writes it to CSV.

## Scope

### contrib/content.py — Pure Functions (3)

| Function | What It Does | Legacy Equivalent |
|----------|-------------|------------------|
| `has_text(html, text, ...)` | Check if HTML content contains a text string | `Card.has_text()` |
| `find_urls(html)` | Extract all URLs (src, href) from HTML | `Card.find_urls()` + `find_urls_in_doc()` |
| `replace_url(html, old_url, new_url)` | Rewrite URLs in HTML content | `Card.replace_url()` |

### contrib/workflows.py — Folder Hierarchy (1)

| Function | What It Does | Legacy Equivalent |
|----------|-------------|------------------|
| `dump_folder_hierarchy(g, collection_id, path)` | Recursively walk folder tree → CSV | `folder_hierarchy.py` customer script |

### Dropped from Backlog

- **`download_resources()`** — Does not exist in legacy py-sdk despite being listed in the audit. No implementation to port.

## Design Decisions

1. **Pure functions take HTML strings**: `has_text`, `find_urls`, `replace_url` operate on raw HTML strings, not Card objects. This makes them usable with any HTML content (cards, pages, drafts) and testable without mocking.
2. **BeautifulSoup for HTML parsing**: Consistent with legacy py-sdk. Used by `find_urls` for reliable attribute extraction.
3. **dump_folder_hierarchy uses folders.items()**: Recursively calls `g.folders.items()` at each level, filters for folder-type items, then `g.folders.get()` for the title. More API calls than the legacy tree-preloading approach, but stays within the public API.
4. **CSV output via csv module**: Standard library, consistent with the legacy customer script.

## Implementation

### New Files
- `src/guru_sdk/contrib/content.py` — 3 pure functions
- `tests/contrib/test_content.py` — tests

### Modified Files
- `src/guru_sdk/contrib/__init__.py` — add content + hierarchy exports
- `src/guru_sdk/contrib/workflows.py` — add dump_folder_hierarchy + _walk_folder_items
- `tests/contrib/test_workflows.py` — add 6 hierarchy tests

## Test Summary

- 28 new tests (586 total)
- has_text: 8 tests (found, case insensitive default, case sensitive, not found, nested, strips tags, empty html, empty search)
- find_urls: 7 tests (href, src, mailto, dedup, empty html, no urls, multiple types)
- replace_url: 7 tests (href, src, all occurrences, no match, returns modified flag, not modified flag, partial match)
- dump_folder_hierarchy: 6 tests (flat folders, nested 3 levels, empty collection, default path, returns path, cards skipped)

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 586 passed
- mypy: ⏭ verify on Mac (segfaults in sandbox)
