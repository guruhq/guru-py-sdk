# guru-py-sdk

Modern Python SDK for the [Guru API](https://developer.getguru.com). Typed, sync-first, async-ready, and architecturally aligned with [guru-cli](https://github.com/guruhq/guru-cli).

## Install

Requires Python 3.10+ and [uv](https://docs.astral.sh/uv/).

```bash
# Install uv (if you don't have it)
brew install uv

# Clone the repo and install
git clone https://github.com/guruhq/guru-py-sdk.git
cd guru-py-sdk
uv sync
```

This creates a `.venv` in the project root with the SDK and all dependencies installed.

## Quick Start

Set your Guru API credentials:

```bash
export GURU_USER="you@company.com"
export GURU_TOKEN="your-api-token"
```

You can find your API token in the Guru web app under **Settings > API Access**.

Then use the SDK:

```python
from guru_sdk import Guru

g = Guru()  # reads GURU_USER + GURU_TOKEN from env

# Collections
collections = g.collections.list()
engineering = g.collections.get("Engineering")  # accepts name or UUID
groups = g.collections.groups(engineering.id)

# Folders
folders = g.folders.list(collection_id=engineering.id)
items = g.folders.items(folders[0].id)

# Cards
card = g.cards.get("card-id-or-title")
tags = g.cards.list_tags(card.id)
comments = g.cards.list_comments(card.id)
```

Run scripts with `uv run` to use the project's virtual environment without activating it:

```bash
uv run python your_script.py
```

Credentials are resolved in order:

1. Explicit arguments: `Guru(username="...", api_token="...")`
2. Environment variables: `GURU_USER` / `GURU_TOKEN`
3. Legacy env vars: `PYGURU_USER` / `PYGURU_TOKEN` (backward compat with `py-sdk`)

## Resources

The SDK uses a resource module pattern — each Guru API area is a separate resource on the client.

### Cards (`g.cards`)

CRUD, verification, tags, comments, folders, collaborators, and more.

```python
card = g.cards.get("card-id")
card = g.cards.create(preferredPhrase="My Card", content="<p>Hello</p>", collection_id="...")

g.cards.verify(card.id)
g.cards.add_tag(card.id, tag_id="...")
g.cards.add_comment(card.id, body="Looks good!")
g.cards.add_to_folder(card.id, folder_id="...")
```

### Folders (`g.folders`)

CRUD, hierarchy traversal, and permissions.

```python
folders = g.folders.list(collection_id="...")
items = g.folders.items(folder_id)
parent = g.folders.parent(folder_id)

perms = g.folders.permissions(folder_id)
g.folders.add_permission(folder_id, group_id="...", role="AUTHOR")
```

### Collections (`g.collections`)

CRUD, group access management, and navigation.

```python
collections = g.collections.list()
collection = g.collections.get("Engineering")  # name or UUID

groups = g.collections.groups(collection.id)
g.collections.add_group(collection.id, group_id="...", role="AUTHOR")

home = g.collections.home_folder(collection.id)
```

### Groups (`g.groups`)

CRUD, member management, and collection access.

```python
groups = g.groups.list()
eng = g.groups.get("Engineering")  # name or UUID

members = g.groups.members(eng.id)
g.groups.add_members(eng.id, emails=["alice@company.com", "bob@company.com"])
g.groups.remove_member(eng.id, email="alice@company.com")

collections = g.groups.collections(eng.id)
```

### Members (`g.members`)

List, search, invite, and remove team members.

```python
all_members = g.members.list()
results = g.members.list(search="alice")
member = g.members.get("alice@company.com")

g.members.invite(email="new@company.com")
g.members.invite(email="new@company.com", member_type="LIGHT", message="Welcome!")
g.members.remove("former@company.com")
```

### Tags (`g.tags`)

Tag and category management. Team ID is resolved automatically.

```python
categories = g.tags.list_categories()
tag = g.tags.get_tag("onboarding")  # name or UUID

g.tags.create_tag(category_id="...", value="new-tag")
g.tags.update_tag(tag.id, value="renamed")

g.tags.create_category(name="Priority")
g.tags.update_category(category_id, name="Severity")
g.tags.delete_category(category_id)
```

### Search (`g.search`)

Keyword and semantic search across cards, sources, and documents.

```python
# Keyword search for cards
cards = g.search.cards("onboarding")
cards = g.search.cards("draft content", query_type="draft", show_archived=True)

# Keyword search across cards + sources
results = g.search.documents("API reference", max_results=10)
print(f"Found {results.total} documents")
for doc in results.documents:
    print(f"  - {doc.title} ({doc.document_type})")

# Semantic (natural language) search
results = g.search.documents_semantic("how do I reset my password")

# Search source records only
results = g.search.sources(search_terms="deploy", source_types=["JIRA"])
```

## Name Resolution

All resources accept either UUIDs or human-readable names. When you pass a name, the SDK resolves it automatically:

```python
# Both work:
g.collections.get("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")
g.collections.get("Engineering")
```

## Error Handling

The SDK raises typed exceptions so you can handle specific failure modes:

```python
from guru_sdk.errors import NotFoundError, AuthenticationError

try:
    card = g.cards.get("nonexistent")
except NotFoundError:
    print("Card not found")
except AuthenticationError:
    print("Check your GURU_USER and GURU_TOKEN")
```

The full hierarchy: `GuruError` > `GuruApiError` (with `status_code`, `message`, `body`) > `AuthenticationError` (401), `ForbiddenError` (403), `NotFoundError` (404), `RateLimitError` (429). Client-side input validation raises `ValidationError`.

## Architecture

Mirrors the guru-cli two-layer pattern:

```
guru-cli (TypeScript)              guru-py-sdk (Python)
─────────────────────              ────────────────────
GuruHttp (transport)        →      HttpClient (httpx sync)
*Resource classes            →      *Resource classes
GuruClient (facade)          →      Guru (facade)
Zod schemas (validation)     →      Pydantic v2 models
```

Resource modules use constructor injection — each receives `HttpClient` and provides typed methods. The `Guru` facade wires them together. Models are Pydantic v2, generated from the Guru public Swagger spec, with `extra="ignore"` for forward compatibility and `frozen=True` for immutability.

## Development

```bash
uv sync --all-extras       # install all deps (runtime + dev + codegen)
make check                 # lint + typecheck + test (run before any PR)
```

Or individually:

```bash
make lint                  # ruff check
make typecheck             # mypy --strict
make test                  # pytest
```

## What's Next

- **Phase 3:** Extended resources — search, sources, drafts, pages, agents, answers, announcements
- **Phase 4:** `contrib/` workflows, publisher, bundle, migration guide, PyPI publish as `guru-sdk`

## License

MIT
