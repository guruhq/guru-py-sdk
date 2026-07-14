# Changelog

All notable changes to guru-py-sdk will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `DraftResource.add_group_collaborators(draft_id, group_ids)` — add User Group
  collaborators to a card draft (mirrors guru-cli's `addGroupCollaborators`).
- `DraftResource.remove_group_collaborator(draft_id, group_id)` — remove a User
  Group collaborator (thin alias over `remove_collaborator`; the collaborator ID
  is the group ID — ADR-014).

### Changed
- **Breaking (minor):** `DraftCollaborator` — renamed the `group` field to
  `user_group` (alias `userGroup`), typed as `UserGroup`. Card drafts return
  group collaborators under `userGroup` (pages use `group` — ADR-014), so
  user-group collaborators now parse correctly. Any caller reading `.group` on a
  card-draft collaborator must switch to `.user_group`.

### Added (foundation)
- Project skeleton: `pyproject.toml`, package structure, CI config
- `GuruModel` base class (Pydantic v2, `extra="ignore"`, `frozen=True`)
- `HttpClient` — synchronous HTTP transport with httpx
- `Guru` client facade with credential resolution (args → env vars → legacy env vars)
- Exception hierarchy: `GuruError`, `GuruApiError`, `NotFoundError`, `AuthenticationError`, `ForbiddenError`, `RateLimitError`, `ValidationError`
- Input validation: `validate_input()` (strict) and `validate_free_text()` (lenient)
- `@deprecated` decorator with removal version and migration guidance
- `_compat.py` helpers: `is_uuid()`, input validation
- `BaseResource` class for resource modules
- `scripts/generate_models.py` stub for Swagger-driven model generation
- Full test suite for all foundation modules
