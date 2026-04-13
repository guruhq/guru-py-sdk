# Bundle — Zip-Based Content Import

The Bundle builds a tree of folders and cards, generates a zip file in Guru's
import format, and uploads it to a collection. Use it when you need to bulk
import content from an external system.

## Prerequisites

```bash
export GURU_USER="you@company.com"
export GURU_TOKEN="your-api-token"
```

---

## Example 1: Simple Import

Create a collection with one folder and two cards.

```python
from guru_sdk import Guru
from guru_sdk.contrib.bundle import Bundle

g = Guru()
bundle = Bundle(g)

# Create a folder node
docs = bundle.node(id="docs", title="Engineering Docs")

# Create card nodes and add them to the folder
bundle.node(
    id="api-guide",
    title="API Guide",
    content="<p>Our API uses REST with JSON responses.</p>",
    tags=["api", "engineering"],
).add_to(docs)

bundle.node(
    id="setup",
    title="Dev Environment Setup",
    content="<p>Clone the repo and run <code>make install</code>.</p>",
    tags=["engineering"],
).add_to(docs)

# Preview the tree structure
bundle.print_tree()

# Generate the zip file
bundle.zip(path="/tmp/my_import")

# Upload to Guru — creates the collection if it doesn't exist
bundle.upload(name="Engineering", color="#1B998B")
```

---

## Example 2: Nested Folders

Three levels of folders with cards at each level.

```python
from guru_sdk import Guru
from guru_sdk.contrib.bundle import Bundle

g = Guru()
bundle = Bundle(g)

# Build a 3-level hierarchy
root = bundle.node(id="product", title="Product Knowledge")

features = bundle.node(id="features", title="Features")
features.add_to(root)

billing = bundle.node(id="billing", title="Billing")
billing.add_to(features)

# Cards at each level
bundle.node(
    id="overview",
    title="Product Overview",
    content="<p>Our product helps teams share knowledge.</p>",
).add_to(root)

bundle.node(
    id="search",
    title="Search Feature",
    content="<p>Search uses AI to find relevant cards.</p>",
).add_to(features)

bundle.node(
    id="pricing",
    title="Pricing Plans",
    content="<p>We offer Starter, Business, and Enterprise plans.</p>",
).add_to(billing)

bundle.zip(path="/tmp/nested")
bundle.upload(name="Product KB")
```

**Note**: Guru's import format supports a maximum folder depth of 3. Folders
deeper than that are automatically removed during `zip()`.

---

## Example 3: Importing from an External API

Pull pages from an external system and build nodes in a loop. The URL-based
ID hashing means the same URL always maps to the same node, so calling
`node()` multiple times with the same URL updates the existing node.

```python
import httpx
from guru_sdk import Guru
from guru_sdk.contrib.bundle import Bundle

g = Guru()
bundle = Bundle(g, skip_empty_folders=True)

# Fetch pages from your external system
api = httpx.Client(base_url="https://docs.internal.com/api")
pages = api.get("/pages").json()

for page in pages:
    node = bundle.node(
        url=page["url"],               # hashed to create a stable ID
        title=page["title"],
        content=page["html_body"],
        tags=page.get("tags", []),
    )

    # Establish parent/child relationships
    if page.get("parent_url"):
        # This creates or finds the parent node — we may not have its
        # content yet, but we can set up the relationship now and fill
        # in the content when we encounter it in the loop.
        parent = bundle.node(url=page["parent_url"], title=page["parent_title"])
        node.add_to(parent)

bundle.zip(path="/tmp/migration")
bundle.upload(name="Imported Docs")
```

---

## Example 4: Sync Mode (Replace Collection Content)

Use `is_sync=True` to replace the entire collection's content instead of
adding to it. Useful for scheduled syncs that should mirror the external
source exactly.

```python
from guru_sdk import Guru
from guru_sdk.contrib.bundle import Bundle

g = Guru()
bundle = Bundle(g, id="weekly_sync")

# ... build your nodes ...

bundle.zip(path="/tmp/sync")
bundle.upload(name="External Docs", is_sync=True)
```

---

## Example 5: Folder with Content

If a folder node also has HTML content, the Bundle automatically creates a
child card to hold it (since folders themselves can't contain HTML in Guru's
import format).

```python
from guru_sdk import Guru
from guru_sdk.contrib.bundle import Bundle

g = Guru()
bundle = Bundle(g)

# This node has both children AND content
section = bundle.node(
    id="onboarding",
    title="Onboarding",
    content="<p>Welcome! Here's what you need to know.</p>",
)

bundle.node(
    id="day1",
    title="Day 1 Checklist",
    content="<p>Set up your laptop, meet your team.</p>",
).add_to(section)

bundle.zip(path="/tmp/onboarding")

# After zip(), the tree looks like:
#   Onboarding (FOLDER)
#     ├── Onboarding (CARD) ← auto-inserted to hold the folder's content
#     └── Day 1 Checklist (CARD)
bundle.print_tree()
```

---

## Example 6: HTML Sanitization

The `clean_html()` function strips non-Guru attributes and filters CSS
classes. It runs automatically on content passed to `node()`, but you can
also use it standalone.

```python
from guru_sdk.contrib.bundle import clean_html

# Strips onclick, data-custom, keeps href and ghq- classes
html = '<a href="/page" onclick="track()" class="ghq-link btn primary">Click</a>'
clean = clean_html(html)
# Result: <a href="/page" class="ghq-link">Click</a>
```

### What clean_html keeps:
- **Attributes**: style, start, href, target, rel, title, src, alt, height, width, class
- **Data attributes**: anything starting with `data-ghq-`
- **CSS classes**: only those starting with `ghq-`

### What it strips:
- All other attributes (onclick, data-custom, id, role, aria-*, etc.)
- All non-Guru CSS classes

To skip sanitization for a specific node, pass `sanitize_html=False`:

```python
bundle.node(
    id="raw",
    title="Pre-cleaned Card",
    content=already_clean_html,
    sanitize_html=False,
)
```

---

## Debugging

Use `print_tree()` to inspect the hierarchy before zipping:

```python
bundle.print_tree()
# Output:
# - Engineering Docs (FOLDER)
#   - API Guide (CARD, url=https://example.com/api)
#   - Dev Setup (CARD)
```

Check `bundle.messages` after operations for a log of what happened:

```python
bundle.zip(path="/tmp/debug")
for msg in bundle.messages:
    print(msg)
```
