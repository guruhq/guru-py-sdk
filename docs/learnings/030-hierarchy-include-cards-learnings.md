# Iteration 030 - Folder Hierarchy: Include Cards - Learnings

## What Went Wrong

1. **A method that is never called live can be broken since day one.** `get_bulk` was ported in iteration 004 with mock-only tests that encoded a guessed contract. The tests passed for months while every real call returned 400. Mocked HTTP tests prove the SDK sends what *we think* the API wants; they prove nothing about what the API accepts.
2. **Read the spec's operation description, not just the schema.** The 50-item cap on `GET /folders/{id}/items` is stated only in the prose `description` ("A maximum of 50 folder items will be returned..."). The response schema is a plain array, so nothing in codegen flags that the endpoint paginates.
3. **The spec under-describes response payloads.** `FolderItem` in the spec has three fields; the live response has ten, including the titles we were making extra calls to fetch. guru-cli had already found this. A raw dump of one live response would have saved a design round.

4. **Mocks encoded our assumption about the paging header, so every pagination test passed while live pagination never advanced.** Guru sends `rel="next-page"`; every test (and the parser) used `rel="next"`. Found only by a live run against a collection bigger than one page (iteration 031).

## Rules Going Forward

- **Any endpoint not in `swagger/swagger.json` needs one live (QA) call before a workflow depends on it.** The legacy py-sdk (`py-sdk/guru/core.py`) is the best source for the contract of these unlisted endpoints; check it when porting.
- **When adding a list method, check the operation description for a page cap or `Link` header and use `get_paginated` if present.** Other `get_list` callers may have the same bug and are worth an audit.
- **Assert exact request bodies** (`== {"ids": [...]}`), not containment (`CARD_UUID in body`). Containment passed for both the wrong and right shapes.
- **Before adding a follow-up lookup for a field, dump one raw live response** and check guru-cli's schema for the same endpoint. The field may already be there.
- **Write mocked headers and bodies from a captured live response, not from memory or the spec.** Anything the API sends in a format we guessed is untested, however many tests touch it.
- **A pagination fix is not done until a live run crosses a page boundary.** Pick a collection whose counts exceed the caps and check that the totals are not exactly a multiple of the page size.
