# Iteration 016 — Bundle (Zip-Based Content Import)

**Status**: Complete
**Date**: 2026-04-13

## Goal

Port the legacy `Bundle` and `BundleNode` classes from `py-sdk/guru/bundle.py` to `contrib/bundle.py`. This is a content import tool that lets customers build a tree of folders and cards, generate a zip file in Guru's import format, and upload it to a collection.

## Architecture

### Two Classes

1. **BundleNode** — a tree node representing a folder or card in the import hierarchy
   - Parent/child relationships with cycle detection
   - HTML content with Guru-specific attribute sanitization
   - URL rewriting for cross-node links and image resources
   - YAML/HTML file generation for the zip format

2. **Bundle** — orchestrator that manages nodes and produces the zip
   - Node registry (create-or-update by ID)
   - Auto type assignment (folder vs card based on tree structure)
   - Structural node insertion (folder-with-content gets a child card)
   - Zip generation (YAML + HTML + resources)
   - Upload to Guru via `/app/contentupload` endpoint (see ADR-005)

### Import Flow
1. Customer creates nodes: `bundle.node(id="x", title="...", content="<p>...</p>")`
2. Establishes parent/child: `child.add_to(parent)`
3. Calls `bundle.zip()` — assigns types, inserts structural nodes, sanitizes HTML, writes files, creates zip
4. Calls `bundle.upload(name="My Collection")` — uploads zip to Guru

### What We're Porting

| Feature | Status | Notes |
|---------|--------|-------|
| BundleNode tree structure | Port | parent/child, add_to, add_child, move_to, detach, cycle detection |
| BundleNode.split / split_all | Drop | Requires BeautifulSoup for CSS selector splitting |
| clean_html (attribute whitelist + class filter) | Port | Guru-specific: strip non-whitelisted attrs, keep only ghq-* classes. Stdlib html.parser. |
| clean_up_html (full BS4 munging) | Drop | Board-era table/list migration, 200+ lines of BS4. Not relevant for new imports. |
| html_cleanup (URL rewriting) | Port | Cross-node link rewriting, image resource handling. Stdlib html.parser. |
| Bundle node management | Port | node(), has_node, remove_node, type assignment, structural insertion |
| Bundle zip generation | Port | YAML + HTML files, zip archive creation |
| Bundle upload | Port | /app/contentupload and /app/contentsyncupload (ADR-005) |
| Bundle.load_html / http_get / http_post | Drop | Convenience HTTP wrappers — customers can use httpx/requests directly |
| Bundle.view_in_browser / build_spreadsheet | Drop | Debug/preview tools, not core functionality |
| Bundle.print_tree | Port | Useful for debugging |
| Event logging to CSV | Simplify | Use messages list (like Publisher), not CSV |

### HTML Sanitization (clean_html)

Two focused operations, ported with stdlib `html.parser`:
1. **Attribute whitelist**: Keep only style, start, href, target, rel, title, src, alt, height, width, class, and data-ghq-* attributes. Strip everything else.
2. **CSS class filter**: Keep only classes prefixed with `ghq-`. Remove all others.

### Zip Format

```
collection.yaml              # {Version: 2, Title: "...", Items: [...], Tags: [...]}
cards/{id}.yaml              # {Title: "...", ExternalId: "...", ExternalUrl: "...", Tags: [...]}
cards/{id}.html              # Card HTML content
folders/{id}.yaml            # {Title: "...", ExternalId: "...", Items: [...]}
resources/{hash}.{ext}       # Downloaded/attached files
```

## Scope

### BundleNode Methods
| Method | Description |
|--------|-------------|
| `add_to(parent)` | Add this node as child of parent |
| `add_child(child, first, after)` | Add child with optional ordering |
| `move_to(parent)` | Detach from all parents, add to new parent |
| `detach()` | Remove from all parents |
| `ancestors()` | List all ancestor nodes |
| `get_children_recursively()` | Flatten subtree |
| `write_files(bundle_path)` | Write YAML + HTML to disk |
| `make_yaml()` | Generate YAML metadata |

### Bundle Methods
| Method | Description |
|--------|-------------|
| `node(id, url, title, content, ...)` | Create or update a node |
| `has_node(id)` | Check if node exists |
| `remove_node(node)` | Remove a node from the bundle |
| `zip(path)` | Assign types, generate files, create zip |
| `upload(name, color, desc, ...)` | Upload zip to Guru collection |
| `print_tree()` | Debug output of hierarchy |

### New: clean_html()
Standalone function in `contrib/bundle.py` (or imported from `contrib/content.py`):
- `clean_html(html: str) -> str` — strip non-whitelisted attributes, filter to ghq-* classes

### Dependencies
- Zero external dependencies (stdlib only: zipfile, hashlib, pathlib, html.parser)
- Guru client only needed for `upload()`

## Test Summary

44 new tests in `tests/contrib/test_bundle.py`:
- **BundleNode tree** (10): add_to, add_child (default/first/after), cycle detection, duplicate noop, detach, move_to, ancestors, get_children_recursively
- **BundleNode YAML** (4): card yaml, folder yaml, no-url, no-tags
- **clean_html** (8): strip unknown attrs, keep whitelist, image attrs, ghq data attrs, css class filter, remove class if no ghq, ol start, empty passthrough
- **Bundle node mgmt** (5): create, update existing, url hashing, title truncation, remove_node
- **Bundle type assignment** (5): children → folder, content → card, folder-with-content insertion, depth limit, skip empty folders
- **Bundle zip** (6): collection.yaml, card files, folder yaml, html content, yaml structure, tags in collection
- **Bundle upload** (5): import, sync, create collection if missing, upload by ID, requires name/id
- **Bundle print_tree** (1): debug output

Total: 655 tests (611 → 655, +44)

## Quality Gates

```
ruff check   ✅ (zero errors)
mypy         ⏭ (segfaults in sandbox — verify on Mac)
pytest       ✅ 655 passed in 9.60s
```
