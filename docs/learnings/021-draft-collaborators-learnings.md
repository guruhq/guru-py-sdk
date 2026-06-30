# Iteration 021 — Draft Collaborators: Learnings

## What Worked

- **Reading guru-cli as the source of truth.** The epic (156474) said "CLI already has
  this functionality," and reading `guru-cli/src/guru/resources/drafts.ts` +
  `types.ts` gave the exact endpoint paths, request body shape, and collaborator schema.
  No guesswork.
- **Mirroring the existing `page_drafts` SDK pattern.** `list_collaborators` /
  `add_collaborators` / `remove_collaborator` already existed for page drafts using
  `get_list` / `post_list` / `delete`. Card-draft collaborators dropped in cleanly using
  the same HttpClient helpers and the same raw-dict argument style.
- **TDD against `pytest-httpx`.** Tests assert both the parsed model and the request body
  wrapping (`{"collaborators": [...]}`), which caught the API contract precisely.

## What Didn't Work

- **Environment bootstrap.** `make check` invokes bare `ruff`/`mypy`/`pytest`, which are
  not on the global PATH — they live in the project venv. First-time setup required
  `brew install uv` then `uv sync --all-extras`, after which `uv run make check` works.
  (Recorded so future first-time contributors don't hit the same wall.)

## Patterns That Emerged

- **Card drafts and page drafts have parallel-but-not-identical collaborator surfaces.**
  - Card draft (`DraftResource`): list / add / remove. Collaborator has `dateCreated`,
    no `objectRole`.
  - Page draft (`PageDraftResource`): list / add / **update** / remove. Collaborator has
    `objectRole`, no `dateCreated`.
  When extending one, do NOT blindly copy the other — confirm the CLI schema for each.

## What We'd Do Differently

- Nothing material. The match-the-CLI approach kept scope tight and the diff small
  (one model, three methods, nine tests).
