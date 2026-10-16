# Iteration 030 - Folder Hierarchy: Include Cards + Tree Rendering

**Date**: 2026-10-16
**Status**: Complete

## Goal

Let `dump_folder_hierarchy` list cards alongside folders, so a customer can get a complete collection listing (folders and the cards inside them) from one call.

## What We Built

- **`dump_folder_hierarchy(..., include_cards=False)`** in `src/guru_sdk/contrib/workflows.py`. Default output is unchanged (folders only, one column per path level). With `include_cards=True`, every row starts with a `type` column (`folder` or `card`) followed by the path, ending in the item's title. Rows follow walk order, so each card appears directly under its folder. No UUID column, by request: the output is meant for people reading it in a spreadsheet.
- **Titles come from the folder listing itself.** The live `GET /folders/{id}/items` payload carries `title` on folders and `preferredPhrase` on cards, though the spec's `FolderItem` lists neither (confirmed on QA; guru-cli already relies on it). New `FolderItemDetail` in `models/_manual.py` subclasses `FolderItem` with those two fields, and `items()` returns it. The walk now makes one `items()` call per folder and nothing else. `folders.get()` and `cards.get_bulk()` remain only as fallbacks for an item that arrives without a title; a card still untitled after that is listed by its ID.
- **`FolderResource.items()` now paginates.** `GET /folders/{id}/items` returns at most 50 items per page with a `Link` header to the next page. `items()` used `get_list`, so every folder was silently truncated at 50 items. It now uses `get_paginated` (`max_pages=10`, 500 items) and returns a `PaginatedList` whose `complete` flag reports truncation. This also fixes `replace_text_in_collection_cards`, which was silently skipping cards past the 50th in any folder.
- **`CardResource.get_bulk()` fixed.** It had never worked against the live API. `POST /cards/bulk` is not in the Swagger spec. The SDK sent a bare JSON array and parsed a list; the real contract (from the legacy py-sdk `get_cards`, confirmed on QA) is a body of `{"ids": [...]}` and a response dict keyed by card ID, each entry carrying a per-card HTTP `status`. QA returned `400 "Error parsing JSON body"` for the old body. `get_bulk` now sends the object, returns cards in request order, omits IDs missing from the response or with a non-2xx entry status, and makes no request for an empty list.
- **`render_hierarchy(csv_path, format="text" | "mermaid", root_name=None, path=None)`** in a new `src/guru_sdk/contrib/hierarchy.py`. Pure function, no API calls, so it lives beside `content.py` rather than in `workflows.py` (whose functions all take a `Guru` client). Reads either CSV layout; the folders-only layout is detected because it always contains a one-cell row (the first top-level folder), while typed rows always have at least two cells. `text` produces a `tree`-style listing with folders marked 📁; `mermaid` produces a mindmap with folders as boxes and cards rounded, double quotes escaped as `#quot;`. Returns the string and optionally writes it to `path`; Mermaid written to a `.md` file is wrapped in a ```` ```mermaid ```` fence so GitHub and editors render it. `root_name` defaults to the CSV filename minus `_folder_hierarchy.csv`.

## What Changed From Plan

- Planned output was `type,id,path` with a `/`-joined path. Changed to `type` plus one column per level: `/` in titles (e.g. "CI/CD") made a joined path ambiguous, and per-level columns keep the visual indent in a spreadsheet. The ID column was dropped.
- The first version fetched titles with `folders.get()` per folder and `cards.get_bulk()` per folder with cards. A follow-up QA check of the raw items payload showed both titles were already there, cutting the walk from up to three calls per folder to one. `cardDetail=NONE` drops cards from the response entirely, so `items()` keeps the default (`BASIC`).
- `render_hierarchy` was added mid-iteration after the first real CSV came back, to make the output viewable as a tree.
- The pagination and `get_bulk` fixes were not in the original scope. Pagination surfaced while reading the spec for `items()`; the `get_bulk` bug surfaced on the first QA run.
- `get_bulk`'s existing tests asserted the broken contract (they checked only that the ID appeared somewhere in the body and mocked a list response). They were rewritten to the verified contract.

## QA Verification

Read-only script against QA collection "spreadsheet Import": bulk response is a dict keyed by the requested IDs, entries carry `status: 200`, 9 of 9 cards returned, titles match `cards.get()`. Pagination across more than 50 items was **not** exercised live (largest folder had 9 cards); it is covered by mocked `Link`-header tests only.

## Tests

- `tests/resources/test_folders.py`: `items()` follows `Link` pages; reports `complete=False` when capped; parses `title` / `preferredPhrase` into `FolderItemDetail`.
- `tests/resources/test_cards.py`: `get_bulk` sends `{"ids": [...]}`, parses dict response, preserves request order, omits missing IDs, skips non-2xx entries, no request for empty input.
- `tests/contrib/test_hierarchy.py`: text tree connectors, folders-only detection (including a folder titled "card"), empty CSV, default root name, Mermaid shapes and quote escaping, file output (fenced for `.md`, raw otherwise), unknown format.
- `tests/contrib/test_workflows.py`: no card lookups by default; typed rows in walk order (bulk response deliberately reversed); inline titles skip all lookups; `get_bulk` only for cards missing a title; one `get_bulk` per folder in the fallback path; ID fallback for a missing title.

745 tests total. `make check` clean.
