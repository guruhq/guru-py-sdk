# ADR-004: Repo Name vs Package/Import Name

**Date**: 2026-04-09
**Status**: Accepted

## Context

The repository is named `guru-py-sdk` to distinguish it from the TypeScript CLI (`guru-cli`) and the legacy Python SDK (`py-sdk`) at the GitHub organization level. However, inside the Python ecosystem — the package name on PyPI, the import statement, and all internal references — the `py` prefix is redundant. You're already in Python. Repeating it everywhere adds noise without information.

## Decision

Use `guru-py-sdk` for the repo name only. Everything inside the Python ecosystem uses the shorter name:

| Scope | Name | Rationale |
|-------|------|-----------|
| GitHub repo | `guruhq/guru-py-sdk` | Distinguishes from `guru-cli` and `py-sdk` in the org |
| PyPI package | `guru-sdk` | What users type in `uv add guru-sdk` |
| Python import | `guru_sdk` | What users type in `from guru_sdk import Guru` |
| CLAUDE.md heading | `guru-py-sdk` | Matches the repo — this is the project name |
| Internal code | `guru_sdk` | Package name, no prefix needed |

The repo name is an organizational label. The package name is a developer interface. They serve different audiences and don't need to match.

## Consequences

**Positive:**
- Clean developer experience: `from guru_sdk import Guru` is concise and obvious
- No `py` stutter in code — once you're writing Python, the language is implied
- `pip install guru-sdk` / `uv add guru-sdk` is short and memorable
- Zero collision with the legacy `pip install guru` (import `guru`) — both can be installed side-by-side

**Negative:**
- Mild confusion if someone sees `guru-sdk` on PyPI and looks for a `guru-sdk` repo (they'll find `guru-py-sdk`). The `pyproject.toml` URLs point to the correct repo.
