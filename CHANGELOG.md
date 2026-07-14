# Changelog

All notable changes to guru-py-sdk will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

### Fixed
- Ship the PEP 561 `py.typed` marker so downstream type checkers (mypy/pyright)
  resolve SDK types instead of `Any`
