# Learnings — Iteration 011: Pages + Page Drafts

## What Worked

1. **Largest iteration yet, still clean**: 20 methods across 2 resources, 61 tests, 3 manual models. The established patterns (resource module, TDD, validation) scaled well to a bigger scope.

2. **Manual models for internal API**: Creating `_manual.py` for models not in Swagger was the right call. Using the generated `Page` model for page drafts would have silently dropped `pageId` and `createdBy` — a real usability gap that callers would hit immediately.

3. **Pattern reuse from DraftResource**: PageDraftResource follows the same structure as DraftResource — same list/get/create/delete pattern, same validation approach, same body-building convention. The code wrote itself.

## What We Learned

1. **Internal API needs its own model layer**: When endpoints aren't in the Swagger spec, the generated models may not match the actual response shapes. A `_manual.py` file alongside `_generated.py` provides a clean home for hand-written models that follow the same GuruModel conventions.

2. **Ruff TCH001 vs Pydantic runtime needs**: Pydantic models need their type references available at runtime (not just TYPE_CHECKING). The per-file-ignores pattern (`"_manual.py" = ["TCH001"]`) matches what we already do for `_generated.py` with TCH003. This is a recurring tension between type-checking best practices and Pydantic's runtime validation.

3. **Page draft update vs card draft update**: guru-cli includes update for page drafts but omits it for card drafts. The MPS/YJS collaborative editing constraint applies to both, but the guru-cli team made different decisions. We followed their lead — include page draft update, defer card draft update. Worth revisiting if the same "politely fail" architecture is needed for both.

4. **Move method has special validation**: The `prev_sibling_page_id` parameter accepts position anchors ("first", "last") that aren't UUIDs. These must bypass `validate_input()`. The guru-cli uses the same pattern — check for known keywords before validating.

## Patterns Confirmed

- **builtins.list shadowing**: Both new resource classes have `list()` methods, both correctly use `import builtins` in TYPE_CHECKING and `builtins.list[...]` in subsequent annotations. The CLAUDE.md pattern documentation prevented the mypy issues we hit in earlier iterations.
- **Keyword-only create/update args**: Consistent with all other resources. No positional args for write operations.
- **Manual model convention**: `models/_manual.py` — same GuruModel base, same field alias convention, same `extra="ignore"` for forward compat.
