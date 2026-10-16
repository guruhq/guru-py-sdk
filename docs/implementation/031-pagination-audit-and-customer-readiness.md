# Iteration 031 - Pagination Audit + Customer Readiness

**Date**: 2026-10-16
**Status**: Complete

## Goal

Close backlog 030a (audit every `get_list` caller for the 50-item cap that hit `folders.items()`), and make a fresh clone usable by a customer driving it from Claude Code.

## Pagination Audit

Every `get_list` call was checked against its endpoint's operation description in `swagger/swagger.json`. Three more endpoints state a page cap and link to the next page:

| Endpoint | Cap | Fixed callers |
|---|---|---|
| `GET /folders` | 110 | `folders.list()`, folder name resolution, `collections.home_folder()` |
| `GET /cards/verificationmgr` | 50 | `cards.list_unverified()`, card name resolution |
| `GET /cards/{id}/comments` | 25 | `cards.list_comments()` |

`GET /collections` states no cap, but guru-cli paginates it, and `get_paginated` behaves like `get_list` when no `Link` header is sent, so `collections.list()` and collection name resolution follow pages too.

Two caps, by purpose:

- **Plain lists** (`list()`, `list_unverified()`, `list_comments()`) take `max_pages=10` and return a `PaginatedList` whose `complete` flag reports truncation. `PaginatedList` subclasses `list`, so callers are unaffected.
- **Lookups whose miss raises `NotFoundError`** (name resolution, `home_folder()`) read up to `RESOLVE_MAX_PAGES = 100` (`resources/_base.py`). Stopping at 10 would reject names that exist. This is the rule guru-cli recorded in `docs/reference/patterns.md`.

`home_folder()` was the most consequential: `dump_folder_hierarchy` starts there, and a collection with more than 110 folders could fail with "No home folder found".

The other endpoints either state no cap in the spec or are not in the spec at all; guru-cli does not paginate any of the unlisted ones the SDK uses.

## Truncation in the Collection Walks

Review on #16 added a check to `dump_folder_hierarchy`: if `folders.items()` reports `complete=False` (a folder past its 500-item cap), raise `GuruError` instead of writing a partial CSV. `replace_text_in_collection_cards` walked folders the same way and ignored the flag, so it could skip cards and still report success.

Because that workflow edits as it walks, raising mid-walk would leave earlier folders changed and the results list lost. It now runs in two passes: `_collect_card_ids` walks the whole tree first (raising on truncation before any card is read or patched), then `_replace_text_in_card` processes each card. Result order and the one-visit-per-card rule are unchanged. Both walks share `_complete_folder_items`.

## Customer Readiness

- **README**: install from source (`git clone` + `uv sync`), since `pip install guru-sdk` fails until the package is on PyPI; a short "Using it with Claude Code" section.
- **AGENTS.md** (`CLAUDE.md` is a symlink to it): a new top section telling an agent that a session in a fresh clone is usually someone *using* the SDK. Write scripts in `scripts/`, use `contrib/` first, take credentials from env vars, ask before writes, and skip the TDD, `make check` and docs rules, which apply only to SDK changes.

## Found, Not Fixed

Card name resolution matches titles against `/cards/verificationmgr`, which lists only cards needing verification, so a verified card can never be resolved by title. Logged as backlog 031a.

## Tests

9 new tests at the HTTP layer with `Link` headers (stubbing the resource can't catch truncation): `folders.list()`, folder resolution past 10 pages, `collections.list()`, collection resolution, `home_folder()` on page 2, `list_unverified()`, `list_comments()` (plus status on the first page), card resolution. Plus 2 replace-text tests: truncation aborts before any edit, and results keep walk order. 757 tests total.
