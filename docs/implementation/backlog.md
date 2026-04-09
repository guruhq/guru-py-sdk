# Iteration Backlog

The planned iterations for guru-py-sdk, derived from the [restructure plan](/RESTRUCTURE_PLAN.md). Each iteration gets its own `NNN-*.md` file when work begins (via the `start-iteration` skill).

## Completed

| # | Title | Status | Summary |
|---|-------|--------|---------|
| 001 | Foundation | Complete | HttpClient, Guru facade, GuruModel, errors, validation, deprecation, 95 tests, AI-native repo setup |
| 002 | Swagger Model Generation | Complete | Full generation pipeline (253 schemas → 248 models + 122 enums), 6 deprecated schemas filtered, 42 new tests (137 total) |
| 003 | Snake_case Field Aliasing | Complete | Added `--snake-case-field` to codegen, re-generated models with Pythonic field names + camelCase aliases, 5 new tests (142 total) |

## Phase 2 — Core Resources + Generated Models

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 003 | Snake_case Field Aliasing | Post-process generated models to use snake_case field names (e.g., `preferred_phrase`) with camelCase aliases (`preferredPhrase`). Must happen before resource modules start using field names — changing later would be a breaking change for consumers. Update generation pipeline, re-generate, update tests. | 002 |
| 004 | Cards Resource | CardResource — full CRUD, verify/unverify, tags, comments, collaborators, folder placement. Proves the end-to-end pattern: model + resource + tests + wired into Guru facade. Most complex resource, highest usage. | 002, 003 (needs Card model with snake_case fields) |
| 005 | Folders + Collections | FolderResource — CRUD, items, permissions, home folder. CollectionResource — CRUD, group access. Validates that the pattern from 004 is repeatable with simpler resources. | 002, 003 (needs Folder, Collection models with snake_case fields) |
| 006 | Groups + Members + Tags | GroupResource — CRUD, member management. MemberResource — list, get, invite. TagResource — CRUD, categories. Rounds out the core resources. | 002, 003 |

## Phase 3 — Extended Resources

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 007 | Search | SearchResource — keyword + semantic search for cards, sources, documents. Mode/strategy routing mirroring guru-cli's search rebuild (ADR-015). | 002, 003 |
| 008 | Sources | SourceResource — get, object types, facet discovery, facet hierarchy traversal. | 002, 003 |
| 009 | Drafts | DraftResource — CRUD, publishing context, collaborators. | 004 (drafts relate to cards) |
| 010 | Pages + Page Drafts | PageResource — CRUD, position, permissions, nested tree. PageDraftResource — CRUD, collaborators. Internal API (mirrors guru-cli ADR-014). | 002, 003 |
| 011 | Agents + Answers + Announcements | AgentResource (Knowledge Agents) — CRUD, group access, pages. AnswerResource — ask, ask-minimal. AnnouncementResource — create, stats. | 002, 003 |

## Phase 4 — Contrib + Polish

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 012 | Publisher | Port `publish_folders.py` → `contrib/publisher.py`. Folder-based content sync, modernized with Guru client + Pydantic models + pathlib. | 004, 005 (needs cards + folders) |
| 013 | Bundle | Port `bundle.py` → `contrib/bundle.py`. Export/bundle, modernized. | 004, 005 |
| 014 | Migration Guide + PyPI Publish | `docs/migration.md` (v1 → v2 method mapping), README polish, PyPI publish as `guru-sdk`. | All above |

## Notes

- Iterations 003–005 can potentially run in parallel once 002 is complete (they're independent resource modules).
- Iteration numbers are provisional — actual numbers are assigned when work begins. If a new iteration is needed (e.g., a refactor discovered during 003), it gets the next available number.
- Each iteration follows the compound engineering loop: `start-iteration` → TDD → ADRs as needed → `complete-iteration` (implementation record + learnings + architecture update + CLAUDE.md patterns).
