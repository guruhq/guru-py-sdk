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

## Live Pagination Never Worked: `rel="next-page"`

The live check (backlog 030b) on QA collection "Even BIGGER Collection (slab importer 2)" returned exactly 110 folders and a 50-item root folder, the two page caps, and the export wrote 50 of about 109 folders without raising. Raw headers showed why: Guru sends

```
Link: <https://qaapi.getguru.com/api/v1/folders/<id>/items?token=...>; rel="next-page"; title="Next Page"; type="application/json"
```

and `_parse_link_header` matched only `rel="next"`, so every first page was treated as the last. This affected every `get_paginated` caller since iteration 001, including `members.list`, `search` and `bulk_get_comments`, not just the 030/031 fixes. The truncation guards could not catch it: an unreadable header is indistinguishable from a complete result. guru-cli fixed the same thing on 2026-07-20 (`cee35c1`). The pattern now accepts `next` or `next-page`.

## Models Stricter Than Live Data

With pagination working, the same live run reached page 2 of `GET /folders` and failed validation: a folder's `lastModifiedBy` was a pending invite with no `firstName`/`lastName`, both required by the spec. This would have made `folders.list()` and `collections.home_folder()` fail on this collection, which worked on `main` only because pagination never reached page 2. Fixed with a targeted codegen override (`OPTIONAL_FIELD_OVERRIDES`, ADR-009); regenerating on datamodel-code-generator 0.81 changed only those two fields.

## Walk Page Cap

The next live run reached all 3,091 folders (29 pages of `/folders`) and the truncation guard fired on the collection root: more than 500 items, `items()`' default of 10 pages. A walk that must be complete now asks for `_WALK_MAX_PAGES = 200` pages (10,000 items per folder), keeping the guard as the backstop, and the error states the limit. The SDK has no retry on 429; a long walk that is rate-limited stops with `RateLimitError`. Not addressed until seen live.

## Call Budget for the Export

With every fix in place, a full export of the 3,091-folder QA collection would make about 3,100 sequential API calls to produce a listing no one can read. `dump_folder_hierarchy` now takes `max_calls` (default 200; `None` for no limit). The walk opens folders breadth-first so the budget covers the top levels first, then writes rows in tree order. A folder the budget didn't reach still gets its row (its title comes from the parent's listing) plus, with `include_cards`, a marker row `["more", *path, "contents not listed (N cards)"]`, using the live `numberOfFacts` count now on `FolderItemDetail`. A `UserWarning` reports how many folders were left out. The budget counts pages, not folders, via a new `PaginatedList.pages`. A depth limit was considered and dropped: Guru folders nest at most 3 levels.

When the budget is hit, the warning states it plainly ("call budget of 200 reached; this collection is too large to process in full", with counts), and `render_hierarchy`'s text tree ends with the same note whenever the CSV has marker rows, so the call-out survives into the file people share. Folders-only CSVs carry no type column, so they get the warning but no in-file marker.

Live run at the default budget: 230 HTTP requests in 30s (200 for the walk, 29 for `home_folder()` reading every `/folders` page, 1 for collection resolution); 1,671 folder rows, 876 cards, 1,507 folders marked not opened, warning shown. The 29-call lookup is backlog 031b.

Sizing on the QA collection: 1,670 top-level folders (34 pages for the root alone), 3,091 overall. At the default budget every top-level folder gets a row, about 166 are opened, and the rest are marked.

## Truncation in the Collection Walks

Review on #16 added a check to `dump_folder_hierarchy`: if `folders.items()` reports `complete=False` (a folder past its 500-item cap), raise `GuruError` instead of writing a partial CSV. `replace_text_in_collection_cards` walked folders the same way and ignored the flag, so it could skip cards and still report success.

Because that workflow edits as it walks, raising mid-walk would leave earlier folders changed and the results list lost. It now runs in two passes: `_collect_card_ids` walks the whole tree first (raising on truncation before any card is read or patched), then `_replace_text_in_card` processes each card. Result order and the one-visit-per-card rule are unchanged. Both walks share `_complete_folder_items`.

## Customer Readiness

- **README**: install from source (`git clone` + `uv sync`), since `pip install guru-sdk` fails until the package is on PyPI; a short "Using it with Claude Code" section.
- **AGENTS.md** (`CLAUDE.md` is a symlink to it): a new top section telling an agent that a session in a fresh clone is usually someone *using* the SDK. Write scripts in `scripts/`, use `contrib/` first, take credentials from env vars, ask before writes, and skip the TDD, `make check` and docs rules, which apply only to SDK changes.

## Found, Not Fixed

Card name resolution matches titles against `/cards/verificationmgr`, which lists only cards needing verification, so a verified card can never be resolved by title. Logged as backlog 031a.

## Tests

9 new tests at the HTTP layer with `Link` headers (stubbing the resource can't catch truncation): `folders.list()`, folder resolution past 10 pages, `collections.list()`, collection resolution, `home_folder()` on page 2, `list_unverified()`, `list_comments()` (plus status on the first page), card resolution. Plus 2 replace-text tests: truncation aborts before any edit, and results keep walk order. Plus 3 HTTP tests using the live `next-page` header format, and 3 model tests for the `User` override. 777 tests total.
