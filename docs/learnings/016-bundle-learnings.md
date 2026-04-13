# Iteration 016 — Bundle (Zip-Based Content Import) — Learnings

## What Worked

1. **Dropping BeautifulSoup entirely**: The legacy Bundle had two separate HTML processing stages: `clean_up_html()` (200+ lines of BS4 munging from the board-to-folder migration era) and `html_cleanup()` (URL rewriting for cross-node links). We replaced the first with a focused 2-operation `clean_html()` using stdlib `html.parser` and deferred the second. This cut the biggest dependency and the most fragile code.

2. **Focused clean_html scope**: Instead of porting all the table/list restructuring from the legacy code, we kept only the two Guru-specific operations: attribute whitelisting and CSS class filtering to `ghq-*`. These encode knowledge customers shouldn't need to figure out themselves. Everything else (strip scripts, remove empty blocks, fix nested lists) can be handled by customers or by Guru's server-side import processing.

3. **pathlib over os.path**: The legacy Bundle used string formatting for all paths (`self.CARD_YAML_PATH % (self.id, node.id)`). Using `pathlib.Path` with `/` operators is cleaner, handles mkdir, and avoids the path manipulation bugs that come from string concatenation.

4. **Minimal YAML serializer**: Rather than adding PyYAML as a dependency, we wrote `_to_yaml()` — a ~50 line serializer that handles exactly the shapes Guru's import format needs (dicts, lists of dicts, lists of strings, scalars). The output matches what PyYAML produces for these specific cases.

5. **ADR for non-public endpoint**: Documenting the `/app/contentupload` decision in ADR-005 before writing code was the right call. It's a deliberate deviation from our "public API only" rule, with clear rationale and mitigation.

## What We Learned

1. **`replace_all` with noqa comments is dangerous**: Using `replace_all` to strip `# noqa: A002` comments from multiple lines collapsed some lines together (the comment was inline, and removing it joined the line with the next). Had to manually fix 3 corrupted lines. Lesson: be careful with `replace_all` on inline comments — the trailing newline may not be preserved as expected.

2. **Type assignment is tree-dependent**: The auto-typing logic (node with children → FOLDER, node with content → CARD) means you can't set `skip_empty_folders` on a node that hasn't been typed yet. The typing and the skip logic happen at different phases — typing during `_assign_types` traversal, skipping during `_make_items_list` (YAML generation). Tests need to account for this phasing.

3. **Upload endpoint URL construction**: The `/app/contentupload` route uses the same host as the API but a different path prefix. We derive it by stripping `/api/v1` from the base URL. This is fragile if the base URL format changes, but it's the same approach the legacy SDK uses and matches how the web app constructs these URLs.

4. **Folder depth limit is structural, not configurable**: `MAX_FOLDER_DEPTH = 3` is baked into Guru's import format, not a user preference. Folders at depth 3+ cause import failures. The legacy code and our port both enforce this by marking deep nodes as removed.

## What We Dropped (and Why)

- **`split()` / `split_all()`**: CSS selector-based content splitting requires BeautifulSoup. Customers can split content before building nodes.
- **`clean_up_html()`**: 200+ lines of board-era HTML restructuring. Irrelevant for new imports.
- **`load_html()` / `http_get()` / `http_post()` / `download_file()`**: Convenience HTTP wrappers. Customers can use httpx/requests directly.
- **`view_in_browser()` / `build_spreadsheet()`**: Debug/preview tools. Not core to the import workflow.
- **Event logging to CSV**: Replaced with `messages` list (matches Publisher pattern). Simpler and more testable.

## Patterns for Future Iterations

- **stdlib html.parser for targeted sanitization**: The `_HtmlSanitizer` pattern (subclass HTMLParser, filter in `handle_starttag`) works well for attribute-level operations without needing a full DOM.
- **Minimal serializers over library dependencies**: For narrow output formats, a purpose-built serializer (like `_to_yaml`) can be cleaner than adding a dependency.
- **ADR-first for deviation decisions**: When breaking a project rule (like "public API only"), write the ADR before the code. It forces you to articulate the tradeoffs.
