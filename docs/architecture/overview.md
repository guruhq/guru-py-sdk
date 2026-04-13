# guru-py-sdk Architecture

**Last updated**: 2026-04-13 (Iteration 012 — Agents + Answers + Announcements)

## Overview

guru-py-sdk is a modern Python SDK for the Guru API. It mirrors the two-layer architecture of guru-cli (TypeScript): a transport layer (`HttpClient`) and resource modules (`*Resource`) composed by a facade class (`Guru`). Models are Pydantic v2, generated from the Guru public Swagger spec.

## System Diagram

```
                          ┌──────────────────────────┐
                          │       Guru (facade)       │
                          │     src/guru_sdk/client   │
                          └────────────┬─────────────┘
                                       │ composes
              ┌────────────────────────┼────────────────────────┐
              │            │           │           │             │
         CardResource  FolderResource  CollectionResource  SearchResource  PageResource  AgentResource  AnswerResource  AnnouncementResource
         (Phase 2 ✓)   (Phase 2 ✓)    (Phase 2 ✓)         (Phase 3 ✓)     (Phase 3 ✓)  (Phase 3 ✓)    (Phase 3 ✓)     (Phase 3 ✓)
              │            │           │           │             │
              └────────────┴───────────┴───────────┴─────────────┘
                                       │
                                       │ uses
                          ┌────────────▼─────────────┐
                          │   HttpClient (transport)  │
                          │     src/guru_sdk/http     │
                          │   httpx.Client (sync)     │
                          └────────────┬─────────────┘
                                       │
                                       │ HTTP + Basic Auth
                                       ▼
                          ┌──────────────────────────┐
                          │   Guru Public API         │
                          │   api.getguru.com/api/v1  │
                          └──────────────────────────┘
```

## Package Structure

```
src/guru_sdk/
├── __init__.py          # Public API exports
├── _version.py          # Version: 0.1.0
├── _compat.py           # UUID detection, input validation
├── _deprecation.py      # @deprecated decorator
├── client.py            # Guru facade
├── http.py              # HttpClient (httpx sync transport)
├── errors.py            # Exception hierarchy
├── models/
│   ├── __init__.py      # Re-exports 46 key models
│   ├── _base.py         # GuruModel (Pydantic v2 base)
│   ├── _generated.py    # 248 models + 122 enums (auto-generated from Swagger)
│   └── _manual.py       # 3 manual models for internal API (PageDraft, PagePermission, PageDraftCollaborator)
├── resources/
│   ├── __init__.py
│   ├── _base.py         # BaseResource
│   ├── agents.py        # AgentResource (CRUD, name resolution, group access)
│   ├── announcements.py # AnnouncementResource (list, create, stats)
│   ├── answers.py       # AnswerResource (ask, ask_minimal)
│   ├── cards.py         # CardResource (CRUD, verify, tags, comments, folders, collaborators)
│   ├── collections.py   # CollectionResource (CRUD, group access, home folder)
│   ├── drafts.py        # DraftResource (CRD — no update due to MPS/YJS collaborative editing)
│   ├── folders.py       # FolderResource (CRUD, hierarchy, permissions, cross-collection move)
│   ├── groups.py        # GroupResource (CRUD, member management, collection access)
│   ├── members.py       # MemberResource (list, get, invite, remove)
│   ├── page_drafts.py   # PageDraftResource (CRUD, collaborators — internal API)
│   ├── pages.py         # PageResource (CRUD, hierarchy, permissions, move — internal API)
│   ├── search.py        # SearchResource (cards, documents, documents_semantic, sources)
│   ├── sources.py       # SourceResource (list, get, object_types, connections)
│   └── tags.py          # TagResource (tag CRUD, category CRUD, team ID resolution)
└── contrib/
    └── __init__.py      # Phase 4: Publisher, Bundle
```

## Tech Stack

| Concern | Choice | Version |
|---------|--------|---------|
| Language | Python | >=3.10 |
| Package manager | uv | latest |
| Build backend | hatchling | latest |
| HTTP client | httpx | >=0.27,<1 |
| Models | Pydantic v2 | >=2.0,<3 |
| Model generation | datamodel-code-generator | >=0.25 (codegen extra) |
| Linting + formatting | ruff | >=0.4 |
| Type checking | mypy (strict) | >=1.10 |
| Testing | pytest + pytest-httpx | >=8.0, >=0.30 |

## Layers

### Layer 1: HttpClient (transport)
Single file (`http.py`). The only place that touches `httpx`. Responsibilities: auth, tracking headers, JSON serialization, Pydantic model validation on responses, Link-header pagination, and typed error mapping. Resource classes never see raw HTTP.

### Layer 2: Resources
One class per Guru API resource. Each receives `HttpClient` via constructor injection. Methods follow consistent naming: `get`, `list`, `create`, `update`, `delete`. Name resolution (ID vs. human-readable name) lives here.

### Layer 3: Guru Facade
Composes all resources. The public entry point. Handles credential resolution (explicit args → env vars → legacy env vars).

### Models
Pydantic v2 models generated from the Guru public Swagger spec. `GuruModel` base class enforces: `extra="ignore"` (forward compat), `frozen=True` (immutable), `populate_by_name=True` (accepts aliases and field names).

### Error Hierarchy
```
GuruError (base)
├── GuruApiError (HTTP errors)
│   ├── AuthenticationError (401)
│   ├── ForbiddenError (403)
│   ├── NotFoundError (404)
│   └── RateLimitError (429)
└── ValidationError (client-side input validation)
```

## Alignment with guru-cli

| guru-cli (TypeScript) | guru-py-sdk (Python) |
|-----------------------|-------------------|
| `GuruHttp` | `HttpClient` |
| `*Resource` classes | `*Resource` classes |
| `GuruClient` facade | `Guru` facade |
| Zod schemas | Pydantic v2 models |
| `outputSuccess(data)` | Native Python objects |
| Exit codes + JSON stderr | Typed exceptions |
