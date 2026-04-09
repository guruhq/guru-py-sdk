# Skill: Add a Resource Module

## When to Use
When adding a new Guru API resource to the SDK (e.g., cards, folders, collections, search).

## Instructions

### 1. Start with tests (TDD)
1. Create `tests/resources/test_<resource>.py`
2. Write tests for: `get`, `list`, `create`, `update`, `delete` (as applicable)
3. Mock HTTP via `pytest-httpx` — no real API calls
4. Cover: happy path, not-found, validation errors, name resolution

### 2. Create the model
1. If models are generated: ensure `scripts/generate_models.py` produces the model, or hand-write if generation isn't ready yet
2. Create `src/guru_sdk/models/<resource>.py` with Pydantic v2 models inheriting from `GuruModel`
3. Export from `src/guru_sdk/models/__init__.py`

### 3. Create the resource
1. Create `src/guru_sdk/resources/<resource>.py`
2. Class receives `HttpClient` in constructor (constructor injection)
3. Follow naming convention: `get`, `list`, `create`, `update`, `delete`
4. Add name resolution via `is_uuid()` + list-and-match for non-UUID inputs
5. Use `validate_input()` for IDs/names, `validate_free_text()` for natural language fields
6. Public methods first, private methods last
7. Section header comments for functional areas

### 4. Wire it up
1. Add the resource to `Guru` in `src/guru_sdk/client.py`
2. Export from `src/guru_sdk/__init__.py` if the model/resource should be public
3. Export from `src/guru_sdk/resources/__init__.py`

### 5. Quality gates
```bash
make check   # lint + typecheck + test — all must pass
```

### 6. Documentation
1. Update `docs/architecture/overview.md` (system diagram, package structure)
2. Add usage examples to `docs/examples/` if this is a key resource
