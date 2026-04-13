# Iteration 014 — Contrib: Content Utilities + Folder Hierarchy — Learnings

## What Worked

1. **stdlib-only HTML parsing**: Using `html.parser.HTMLParser` instead of BeautifulSoup kept the dependency footprint at zero. The legacy py-sdk used BeautifulSoup, but our use cases (text extraction, URL extraction) are simple enough that the stdlib parser handles them cleanly. This means `contrib/content.py` has no external dependencies at all.

2. **Pure functions on strings**: Making content utilities operate on raw HTML strings (not Card objects) was the right call. They're now usable with card content, page content, draft content, or any arbitrary HTML. Testable without any mocking.

3. **Customer script → SDK workflow**: Converting the `folder_hierarchy.py` customer script into `dump_folder_hierarchy` worked well. The key insight was that the legacy script relied on the old SDK's pre-loaded folder tree (`.folders` property), while our SDK uses `folders.items()` which returns flat items. The recursive `_walk_folder_items` helper bridges this gap cleanly.

4. **tuple return for replace_url**: Returning `(html, was_modified)` from `replace_url` gives callers both the result and a modification flag without needing to compare strings. This pattern is better than the legacy `bool` return (which discarded the modified HTML).

## What We Learned

1. **FolderItem.type is an enum, not a string**: The `Type9` enum has `Type9.folder` and `Type9.card` values. Need to import and compare against the enum, not string literals. This is a gotcha that will recur — generated enums have non-obvious names like `Type9`.

2. **Recursive workflows are API-chatty**: `dump_folder_hierarchy` makes one `items()` call + one `get()` call per folder in the tree. For a collection with 100 folders, that's 200+ API calls. This is fine for the public API approach (and matches the CLI's behavior), but worth noting in docs. A future optimization could add a `folders.tree()` method if the API supports it.

3. **ruff import ordering is strict**: `from __future__ import annotations` must be in its own import block with a blank line separating it from stdlib imports. Caught by CI but trivial to fix.

## Patterns for Future Iterations

- **stdlib over third-party for simple parsing**: If `html.parser` can do it, don't add a dependency
- **Tuple returns for mutating functions**: `(result, was_modified)` is cleaner than bool-only returns
- **Recursive helpers with `_` prefix**: Private recursive functions like `_walk_folder_items` keep the public API clean while handling the tree traversal logic
- **Customer scripts as contrib candidates**: Common customer scripts (like folder hierarchy dumps) are great candidates for `contrib/` — they validate the SDK's API surface against real use cases
