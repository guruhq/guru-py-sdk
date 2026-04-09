# Iteration Backlog

The planned iterations for guru-py-sdk, derived from the [restructure plan](/RESTRUCTURE_PLAN.md). Each iteration gets its own `NNN-*.md` file when work begins (via the `start-iteration` skill).

## Completed

| # | Title | Status | Summary |
|---|-------|--------|---------|
| 001 | Foundation | Complete | HttpClient, Guru facade, GuruModel, errors, validation, deprecation, 95 tests, AI-native repo setup |

## Phase 2 — Core Resources + Generated Models

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 002 | Swagger Model Generation | Get `generate_models.py` producing real Pydantic models from the public spec. Download swagger.json, implement the generation pipeline (datamodel-code-generator + post-processing + ruff format), generate initial model set, validate against GuruModel base class. | None |
| 003 | Cards Resource | CardResource — full CRUD, verify/unverify, tags, comments, collaborators, folder placement. Proves the end-to-end pattern: model + resource + tests + wired into Guru facade. Most complex resource, highest usage. | 002 (needs Card model) |
| 004 | Folders + Collections | FolderResource — CRUD, items, permissions, home folder. CollectionResource — CRUD, group access. Validates that the pattern from 003 is repeatable with simpler resources. | 002 (needs Folder, Collection models) |
| 005 | Groups + Members + Tags | GroupResource — CRUD, member management. MemberResource — list, get, invite. TagResource — CRUD, categories. Rounds out the core resources. | 002 (needs Group, Member, Tag models) |

## Phase 3 — Extended Resources

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 006 | Search | SearchResource — keyword + semantic search for cards, sources, documents. Mode/strategy routing mirroring guru-cli's search rebuild (ADR-015). | 002 |
| 007 | Sources | SourceResource — get, object types, facet discovery, facet hierarchy traversal. | 002 |
| 008 | Drafts | DraftResource — CRUD, publishing context, collaborators. | 002, 003 (drafts relate to cards) |
| 009 | Pages + Page Drafts | PageResource — CRUD, position, permissions, nested tree. PageDraftResource — CRUD, collaborators. Internal API (mirrors guru-cli ADR-014). | 002 |
| 010 | Agents + Answers + Announcements | AgentResource (Knowledge Agents) — CRUD, group access, pages. AnswerResource — ask, ask-minimal. AnnouncementResource — create, stats. | 002 |

## Phase 4 — Contrib + Polish

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 011 | Publisher | Port `publish_folders.py` → `contrib/publisher.py`. Folder-based content sync, modernized with Guru client + Pydantic models + pathlib. | 003, 004 (needs cards + folders) |
| 012 | Bundle | Port `bundle.py` → `contrib/bundle.py`. Export/bundle, modernized. | 003, 004 |
| 013 | Migration Guide + PyPI Publish | `docs/migration.md` (v1 → v2 method mapping), README polish, PyPI publish as `guru-sdk`. | All above |

## Notes

- Iterations 003–005 can potentially run in parallel once 002 is complete (they're independent resource modules).
- Iteration numbers are provisional — actual numbers are assigned when work begins. If a new iteration is needed (e.g., a refactor discovered during 003), it gets the next available number.
- Each iteration follows the compound engineering loop: `start-iteration` → TDD → ADRs as needed → `complete-iteration` (implementation record + learnings + architecture update + CLAUDE.md patterns).
