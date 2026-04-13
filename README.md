# guru-py-sdk

Modern Python SDK for the [Guru API](https://developer.getguru.com). Typed, sync-first, async-ready.

## Install

Requires Python 3.10+.

```bash
pip install guru-sdk

# or with uv
uv add guru-sdk
```

## Quick Start

```bash
export GURU_USER="you@company.com"
export GURU_TOKEN="your-api-token"    # Settings > API Access in the Guru web app
```

```python
from guru_sdk import Guru

g = Guru()

# Get a collection by name or UUID
eng = g.collections.get("Engineering")

# List folders, read a card, search
folders = g.folders.list(collection_id=eng.id)
card = g.cards.get("How to deploy")
results = g.search.cards("onboarding")

# AI-powered answers
answer = g.answers.ask("What's our PTO policy?")
```

Credentials resolve in order: explicit arguments → `GURU_USER`/`GURU_TOKEN` env vars → `PYGURU_USER`/`PYGURU_TOKEN` (legacy).

## AI-Native by Design

This SDK is built to be used with AI coding agents. Rather than memorizing the API surface, point your agent at this repo and let it build what you need.

```
You have access to the Guru Python SDK at ./guru-py-sdk.
Read CLAUDE.md for architecture and patterns, then use the SDK
to write a script that exports all cards tagged "onboarding"
to markdown files.
```

The codebase is structured so agents can quickly orient: `CLAUDE.md` documents every pattern and convention, resource modules follow a consistent interface, and Pydantic models provide type safety that agents can lean on. The `docs/examples/` directory has usage patterns, and `docs/migration.md` maps legacy methods to their new equivalents.

If you need a custom integration — syncing Guru content to an external system, bulk-importing from a CSV, automating user provisioning — describe what you want and let your agent compose the right SDK calls. That's how this repo is designed to be used.

## Resources

Every Guru API area is a resource on the client. All accept names or UUIDs.

| Resource | Access | Examples |
|----------|--------|----------|
| Cards | `g.cards` | CRUD, verify, tags, comments, folders, collaborators, PDF export, attachments |
| Folders | `g.folders` | CRUD, hierarchy traversal, permissions |
| Collections | `g.collections` | CRUD, group access, home folder |
| Groups | `g.groups` | CRUD, member management |
| Members | `g.members` | List, search, invite, remove |
| Tags | `g.tags` | Tags and categories |
| Search | `g.search` | Keyword and semantic search across cards, sources, and documents |
| Sources | `g.sources` | Read-only access to external connectors (Confluence, Jira, Slack, etc.) |
| Drafts | `g.drafts` | Create, read, delete card drafts |
| Pages | `g.pages` | CRUD, nested tree, permissions, repositioning |
| Page Drafts | `g.page_drafts` | Create, read, delete, collaborator management |
| Agents | `g.agents` | CRUD and group access for Knowledge Agents |
| Answers | `g.answers` | AI-powered Q&A against the knowledge base |
| Announcements | `g.announcements` | Broadcast cards to groups, track read stats |

## Error Handling

```python
from guru_sdk.errors import NotFoundError, AuthenticationError

try:
    card = g.cards.get("nonexistent")
except NotFoundError:
    print("Card not found")
except AuthenticationError:
    print("Check your credentials")
```

Hierarchy: `GuruError` → `GuruApiError` (`status_code`, `message`, `body`) → `AuthenticationError` (401), `ForbiddenError` (403), `NotFoundError` (404), `RateLimitError` (429). Input validation raises `ValidationError`.

## Contrib

Higher-level utilities built on the core SDK:

```python
from guru_sdk.contrib import move_card_between_folders, batch_add_users_to_group, has_text

# Move a card from one folder to another
move_card_between_folders(g, card_id="...", source_folder_id="...", target_folder_id="...")

# Batch-add users to a group
batch_add_users_to_group(g, group_id="...", emails=["alice@co.com", "bob@co.com"])

# Check if a card contains specific text
if has_text(card.content, "deprecated"):
    print("Card mentions deprecated content")
```

Also includes `PublisherFolders` (sync Guru content to external systems), `Bundle` (bulk zip import), and content utilities (`find_urls`, `replace_url`).

## Migrating from py-sdk

If you're upgrading from the legacy `guru` package, see the [Migration Guide](docs/migration.md).

## Development

```bash
uv sync --all-extras       # install all deps
make check                 # lint + typecheck + test
```

## License

MIT
