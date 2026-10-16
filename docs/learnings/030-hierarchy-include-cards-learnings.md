# Iteration 030 - Folder Hierarchy: Include Cards - Learnings

## What Went Wrong

1. **A method that is never called live can be broken since day one.** `get_bulk` was ported in iteration 004 with mock-only tests that encoded a guessed contract. The tests passed for months while every real call returned 400. Mocked HTTP tests prove the SDK sends what *we think* the API wants; they prove nothing about what the API accepts.
2. **Read the spec's operation description, not just the schema.** The 50-item cap on `GET /folders/{id}/items` is stated only in the prose `description` ("A maximum of 50 folder items will be returned..."). The response schema is a plain array, so nothing in codegen flags that the endpoint paginates.

## Rules Going Forward

- **Any endpoint not in `swagger/swagger.json` needs one live (QA) call before a workflow depends on it.** The legacy py-sdk (`py-sdk/guru/core.py`) is the best source for the contract of these unlisted endpoints; check it when porting.
- **When adding a list method, check the operation description for a page cap or `Link` header and use `get_paginated` if present.** Other `get_list` callers may have the same bug and are worth an audit.
- **Assert exact request bodies** (`== {"ids": [...]}`), not containment (`CARD_UUID in body`). Containment passed for both the wrong and right shapes.
