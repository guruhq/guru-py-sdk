# Iteration Backlog

The planned iterations for guru-py-sdk, derived from the [restructure plan](/RESTRUCTURE_PLAN.md). Each iteration gets its own `NNN-*.md` file when work begins (via the `start-iteration` skill).

## Completed

| # | Title | Status | Summary |
|---|-------|--------|---------|
| 001 | Foundation | Complete | HttpClient, Guru facade, GuruModel, errors, validation, deprecation, 95 tests, AI-native repo setup |
| 002 | Swagger Model Generation | Complete | Full generation pipeline (253 schemas → 248 models + 122 enums), 6 deprecated schemas filtered, 42 new tests (137 total) |
| 003 | Snake_case Field Aliasing | Complete | Added `--snake-case-field` to codegen, re-generated models with Pythonic field names + camelCase aliases, 5 new tests (142 total) |
| 004 | Cards Resource | Complete | CardResource with 32 methods (CRUD, patch, archive/restore, verify, tags, comments, folders, collaborators, PDF, bulk, move), 7 new HttpClient methods, name resolution, py-sdk parity audit, 95 new tests (237 total) |
| 005 | Folders + Collections | Complete | FolderResource (13 methods: CRUD, hierarchy, permissions, cross-collection move) + CollectionResource (9 methods: CRUD, group access, home folder). Fixed color validation and enum parity. 71 new tests (308 total) |
| 006 | Groups + Members + Tags | Complete | GroupResource (9 methods: CRUD, members, collections), MemberResource (4 methods: list/search, get, invite, remove), TagResource (7 methods: tag/category CRUD + team ID caching via WhoAmI). Extended get_paginated with initial params. 63 new tests (371 total) |

## Phase 2 — Core Resources

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| ~~005~~ | ~~Folders + Collections~~ | ~~Moved to Completed~~ | |
| ~~006~~ | ~~Groups + Members + Tags~~ | ~~Moved to Completed~~ | |

## Phase 2.5 — God Class Audit

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 007 | Legacy Guru Class Audit | Systematic audit of every method on py-sdk's `Guru` class. Categorize each as: (a) already covered by a resource, (b) belongs on a resource not yet built, (c) convenience workflow for `contrib/`, (d) local utility (content parsing, URL extraction, etc.), or (e) deprecated/unnecessary. Produces a migration matrix and populates the contrib backlog. | 004, 005, 006 (needs core resources built to know what's covered) |

## Phase 3 — Extended Resources

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 008 | Search | SearchResource — keyword + semantic search for cards, sources, documents. Mode/strategy routing mirroring guru-cli's search rebuild (ADR-015). | 002, 003 |
| 009 | Sources | SourceResource — get, object types, facet discovery, facet hierarchy traversal. | 002, 003 |
| 010 | Drafts | DraftResource — CRUD, publishing context, collaborators. | 004 (drafts relate to cards) |
| 011 | Pages + Page Drafts | PageResource — CRUD, position, permissions, nested tree. PageDraftResource — CRUD, collaborators. Internal API (mirrors guru-cli ADR-014). | 002, 003 |
| 012 | Agents + Answers + Announcements | AgentResource (Knowledge Agents) — CRUD, group access, pages. AnswerResource — ask, ask-minimal. AnnouncementResource — create, stats. | 002, 003 |

## Phase 4 — Contrib + Polish

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 013 | Contrib: Workflows | Convenience workflows extracted from the god class audit (iteration 007). Multi-step operations like `move_card_to_folder` (remove + add), content utilities (`find_urls`, `has_text`, `replace_url`), and any mini-workflows that compose multiple resource calls. Lives in `contrib/`. | 007 (needs audit results) |
| 014 | Publisher | Port `publish_folders.py` → `contrib/publisher.py`. Folder-based content sync, modernized with Guru client + Pydantic models + pathlib. | 004, 005 (needs cards + folders) |
| 015 | Bundle | Port `bundle.py` → `contrib/bundle.py`. Export/bundle, modernized. | 004, 005 |
| 016 | QA Environment Support | Add `base_url` override and `qa=True` convenience flag to `Guru` constructor (matches py-sdk `qa` param → `https://qaapi.getguru.com/api/v1`). Also support `GURU_BASE_URL` env var. | 001 |
| 018 | Codegen Override Mechanism | Add a config file (e.g. `swagger/overrides.json`) to the model generation pipeline that can force specific fields optional, rename types, or skip schemas. Prevents manual fixes (like User.firstName optionality) from being lost on regeneration. Coordinate with backend on Swagger spec accuracy for agent/system users. | 002 |
| 017 | Migration Guide + PyPI Publish | `docs/migration.md` (v1 → v2 method mapping), README polish, PyPI publish as `guru-sdk`. | All above |

## Notes

- Iterations 005–006 can potentially run in parallel (they're independent resource modules).
- Iteration 007 (god class audit) is a natural checkpoint before Phase 3 — it ensures we know what's covered before building more resources, and feeds directly into the contrib layer.
- Iteration numbers are provisional — actual numbers are assigned when work begins. If a new iteration is needed (e.g., a refactor discovered during 004), it gets the next available number.
- Each iteration follows the compound engineering loop: `start-iteration` → TDD → ADRs as needed → `complete-iteration` (implementation record + learnings + architecture update + CLAUDE.md patterns).
