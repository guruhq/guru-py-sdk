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
| 007 | Legacy Guru Class Audit | Complete | Audited 110+ methods across Guru class + 22 data object classes + Publisher, Bundle, util modules. 50% covered by Phase 2, 16% deferred to Phase 3 resources, 14% identified for contrib, 11% deprecated (boards). Produced full migration matrix. |
| 008 | Search | Complete | SearchResource with 4 methods: cards (keyword via GET /search/cardmgr), documents (keyword via POST /search/documents), documents_semantic (NLQ via GET /search/documents), sources (POST /search/sourcemgr). Exported DocumentSearchResponse, NLQSearchResponse, SearchFacets, Document models. 25 new tests (396 total) |
| 009 | Sources | Complete | SourceResource with 5 methods: list, get, object_types, connections, get_connection. Added empty-string rejection to validate_input(). Fixed SyncStatus enum (SYNCED not COMPLETED). Exported GroupedSourceConnection, ObjectType models. 16 new tests (412 total) |
| 010 | Drafts | Complete | DraftResource with 4 methods (CRD, no update): list, get, create, delete. Update deferred due to collaborative editing (MPS/YJS) — drafts opened in web app enter real-time editing state. 14 new tests (426 total) |
| 011 | Pages + Page Drafts | Complete | PageResource (11 methods: CRUD, nested tree, move, permissions) + PageDraftResource (8 methods: CRD + collaborators, no update — MPS/YJS). Manual models for internal API types (PageDraft, PagePermission, PageDraftCollaborator). 58 new tests (484 total) |
| 012 | Agents + Answers + Announcements | Complete | AgentResource (10 methods: CRUD, name resolution, group access), AnswerResource (2 methods: ask, ask_minimal), AnnouncementResource (3 methods: list, create, stats). 51 new tests (535 total) |
| 013 | Contrib: Workflows | Complete | 6 convenience workflow functions in `contrib/workflows.py`: move_card_between_folders, batch_add_users_to_group, add_user_to_groups, remove_user_from_groups, make_collection_with_setup, add_tag_with_auto_create. 23 new tests (558 total) |
| 014 | Contrib: Content + Hierarchy | Complete | 3 pure HTML content functions in `contrib/content.py` (has_text, find_urls, replace_url) + dump_folder_hierarchy workflow. Zero external dependencies — stdlib html.parser only. 28 new tests (586 total) |
| 015 | Publisher | Complete | `CardChanges` frozen dataclass + `PublisherFolders` ABC framework in `contrib/publisher.py`. Folder-based content sync with metadata persistence, change detection, link rewriting, and abstract hooks for external systems. 25 new tests (611 total) |
| 016 | Bundle | Complete | `Bundle` + `BundleNode` classes in `contrib/bundle.py`. Zip-based content import with tree structure, auto type assignment, Guru-specific HTML sanitization (`clean_html`), YAML generation, and upload via `/app/contentupload` (ADR-005). 44 new tests (655 total) |
| 019 | Card Attachments | Complete | `CardResource.upload_file()` + `HttpClient.post_file()`. Multipart file upload via `POST /attachments/upload` (ADR-006). Returns URL for embedding in card HTML. 6 new tests (661 total) |

## Phase 3 — Extended Resources

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| 010a | Draft & Page Draft Updates + Collaborators | DraftResource update and PageDraftResource update (both with MPS/YJS "politely fail" for active editing sessions), card draft publishing context endpoints, card draft collaborator management, page draft update. Requires detecting draft editing state — applies to both card drafts and page drafts. | 010, 011 |
| ~~021~~ | ~~Frameworks~~ | ~~Deferred — not in public spec, not in CLI. See ADR-007.~~ | ~~002, 003~~ |
| ~~019~~ | ~~Card Attachments~~ | ~~Moved to Completed~~ | ~~004 ✅~~ |

## Phase 4 — Contrib + Polish

| # | Title | Scope | Dependencies |
|---|-------|-------|--------------|
| ~~013~~ | ~~Contrib: Workflows~~ | ~~Moved to Completed~~ | ~~007 ✅~~ |
| ~~014~~ | ~~Contrib: Content Utilities~~ | ~~Moved to Completed (expanded to include folder hierarchy)~~ | ~~007 ✅~~ |
| ~~015~~ | ~~Publisher~~ | ~~Moved to Completed~~ | ~~004, 005 ✅~~ |
| ~~016~~ | ~~Bundle~~ | ~~Moved to Completed~~ | ~~004, 005 ✅~~ |
| 017 | QA Environment Support | Add `base_url` override and `qa=True` convenience flag to `Guru` constructor (matches py-sdk `qa` param → `https://qaapi.getguru.com/api/v1`). Also support `GURU_BASE_URL` env var. | 001 |
| 018 | Codegen Override Mechanism | Add a config file (e.g. `swagger/overrides.json`) to the model generation pipeline that can force specific fields optional, rename types, or skip schemas. Prevents manual fixes (like User.firstName optionality) from being lost on regeneration. Coordinate with backend on Swagger spec accuracy for agent/system users. | 002 |
| 020 | Migration Guide + PyPI Publish | `docs/migration.md` (v1 → v2 method mapping from audit matrix), README polish, PyPI publish as `guru-sdk`. | All above |

## Notes

- Phase 2 is complete. Six core resources cover 50% of all legacy py-sdk functionality.
- Iteration 007 (god class audit) confirmed that board operations (11% of methods) should not be implemented.
- Contrib is now split into two iterations: workflows (multi-step API calls) and content utilities (pure functions on HTML).
- The migration matrix in `docs/implementation/007-legacy-audit.md` maps every py-sdk method to its new-SDK equivalent or category.
- Each iteration follows the compound engineering loop: `start-iteration` → TDD → ADRs as needed → `complete-iteration` (implementation record + learnings + architecture update + CLAUDE.md patterns).
