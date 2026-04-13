# Migration Guide: py-sdk → guru-py-sdk

This guide maps every public method from the legacy `guru` package to its equivalent in `guru-py-sdk`. If you're starting fresh, see the [README](../README.md) instead.

## Key Differences

**Architecture**: The legacy SDK used a single `Guru` god class with 110+ methods. The new SDK uses a resource module pattern — `g.cards`, `g.folders`, `g.collections`, etc. — each with focused, typed methods.

**Models**: The legacy SDK used mutable `data_objects` classes with convenience methods baked in. The new SDK uses immutable Pydantic v2 models generated from the Guru Swagger spec. Content utilities that were on data objects (`Card.has_text()`, `Card.find_urls()`) now live in `guru_sdk.contrib`.

**Credentials**: Same env vars (`GURU_USER`/`GURU_TOKEN`), same `Guru()` constructor. Legacy `PYGURU_USER`/`PYGURU_TOKEN` still work as fallback.

**Error handling**: Legacy SDK returned `None` or raised generic exceptions. New SDK raises typed exceptions: `NotFoundError`, `AuthenticationError`, `ForbiddenError`, `RateLimitError`.

**Boards**: All board operations are removed. Boards were replaced by Folders in Guru.

## Cards

| Legacy | New | Notes |
|--------|-----|-------|
| `g.get_card(card)` | `g.cards.get(card_id)` | Accepts name or UUID |
| `g.get_cards(card_ids)` | `g.cards.get_bulk(card_ids)` | |
| `g.get_card_version(card, version)` | `g.cards.get_version(card_id, version)` | |
| `g.make_card(title, content, collection)` | `g.cards.create(preferredPhrase=, content=, collection_id=)` | |
| `g.save_card(card, verify)` | `g.cards.update(card_id, ...)` | Verify is a separate call: `g.cards.verify()` |
| `g.patch_card(card)` | `g.cards.patch(card_id, ...)` | |
| `g.verify_card(card)` | `g.cards.verify(card_id)` | |
| `g.unverify_card(card)` | `g.cards.unverify(card_id)` | |
| `g.archive_card(card)` | `g.cards.archive(card_id)` | |
| `g.restore_card(card)` | `g.cards.restore(card_id)` | |
| `g.find_card(**kwargs)` | `g.search.cards(query)` | Uses SearchResource |
| `g.find_cards(...)` | `g.search.cards(query)` | Uses SearchResource |
| `g.upload_file(filename)` | `g.cards.upload_file(file_path)` | Returns URL for embedding in card HTML |
| `g.download_card_as_pdf(card, filename)` | `g.cards.download_pdf(card_id)` | Returns bytes; write to file yourself |
| `g.favorite_card(card)` | `g.cards.favorite(card_id)` | |
| `g.unfavorite_card(card)` | `g.cards.unfavorite(card_id)` | |

## Card Comments

| Legacy | New |
|--------|-----|
| `g.add_comment_to_card(card, comment)` | `g.cards.add_comment(card_id, body=)` |
| `g.get_card_comments(card)` | `g.cards.list_comments(card_id)` |
| `g.update_card_comment(comment)` | `g.cards.update_comment(card_id, comment_id, body=)` |
| `g.resolve_card_comment(comment)` | `g.cards.resolve_comment(card_id, comment_id)` |
| `g.reopen_card_comment(comment)` | `g.cards.unresolve_comment(card_id, comment_id)` |
| `g.delete_card_comment(card, comment_id)` | `g.cards.delete_comment(card_id, comment_id)` |

## Collections

| Legacy | New |
|--------|-----|
| `g.get_collection(collection)` | `g.collections.get(collection_id)` |
| `g.get_collections()` | `g.collections.list()` |
| `g.make_collection(name, ...)` | `g.collections.create(name=, ...)` |
| `g.delete_collection(collection)` | `g.collections.remove(collection_id)` |
| `g.get_groups_on_collection(collection)` | `g.collections.groups(collection_id)` |
| `g.add_group_to_collection(group, collection, role)` | `g.collections.add_group(collection_id, group_id=, role=)` |
| `g.remove_group_from_collection(group, collection)` | `g.collections.remove_group(collection_id, group_id=)` |

## Folders

| Legacy | New |
|--------|-----|
| `g.get_folder(folder)` | `g.folders.get(folder_id)` |
| `g.get_folders(collection)` | `g.folders.list(collection_id=)` |
| `g.get_folder_items(folder_id)` | `g.folders.items(folder_id)` |
| `g.add_folder(title, collection, parent)` | `g.folders.create(title=, collection_id=, parent_folder_id=)` |
| `g.delete_folder(folder)` | `g.folders.remove(folder_id)` |
| `g.get_parent_folder(folder)` | `g.folders.parent(folder_id)` |
| `g.get_home_folder(collection)` | `g.collections.home_folder(collection_id)` |
| `g.get_shared_folder_groups(folder)` | `g.folders.permissions(folder_id)` |
| `g.add_shared_folder_group(folder, group)` | `g.folders.add_permission(folder_id, group_id=, role=)` |
| `g.remove_shared_folder_group(folder, group)` | `g.folders.remove_permission(folder_id, group_id=)` |
| `g.move_folder_to_collection(folder, collection)` | `g.folders.move_to_collection(folder_id, collection_id=)` |
| `g.add_card_to_folder(card, folder)` | `g.cards.add_to_folder(card_id, folder_id=)` |
| `g.remove_card_from_folder(card, folder)` | `g.cards.remove_from_folder(card_id, folder_id=)` |
| `g.get_folders_for_card(card)` | `g.cards.list_folders(card_id)` |
| `g.move_card_to_folder(card, src, dst)` | `from guru_sdk.contrib import move_card_between_folders` |
| `g.move_card_to_collection(card, collection)` | `g.cards.move_to_collection(card_id, collection_id=)` |

## Groups

| Legacy | New |
|--------|-----|
| `g.get_group(group)` | `g.groups.get(group_id)` |
| `g.get_groups()` | `g.groups.list()` |
| `g.make_group(name)` | `g.groups.create(name=)` |
| `g.delete_group(group)` | `g.groups.remove(group_id)` |
| `g.get_group_members(group)` | `g.groups.members(group_id)` |

## Members

| Legacy | New |
|--------|-----|
| `g.get_members(search)` | `g.members.list(search=)` |
| `g.invite_user(email, *groups)` | `g.members.invite(email=)` |
| `g.add_user_to_group(email, group)` | `g.groups.add_members(group_id, emails=[email])` |
| `g.remove_user_from_group(email, group)` | `g.groups.remove_member(group_id, email=)` |
| `g.remove_user_from_team(email)` | `g.members.remove(email)` |
| `g.add_users_to_group(emails, group)` | `from guru_sdk.contrib import batch_add_users_to_group` |
| `g.add_user_to_groups(email, *groups)` | `from guru_sdk.contrib import add_user_to_groups` |
| `g.remove_user_from_groups(email, *groups)` | `from guru_sdk.contrib import remove_user_from_groups` |

## Tags

| Legacy | New |
|--------|-----|
| `g.get_tag(tag)` | `g.tags.get_tag(tag_id)` |
| `g.get_tags()` | `g.tags.list_categories()` |
| `g.get_tag_categories()` | `g.tags.list_categories()` |
| `g.make_tag(tag)` | `g.tags.create_tag(category_id=, value=)` |
| `g.add_tag_to_card(tag, card)` | `g.cards.add_tag(card_id, tag_id=)` |
| `g.remove_tag_from_card(tag, card)` | `g.cards.remove_tag(card_id, tag_id=)` |

## Search

| Legacy | New |
|--------|-----|
| `g.find_card(**kwargs)` | `g.search.cards(query)` |
| `g.find_cards(...)` | `g.search.cards(query)` |
| — | `g.search.documents(query)` |
| — | `g.search.documents_semantic(query)` |
| — | `g.search.sources(search_terms=)` |

## Drafts

| Legacy | New |
|--------|-----|
| `g.get_drafts(card)` | `g.drafts.list(card_id=)` |
| `g.create_draft(title, content)` | `g.drafts.create(title=, content=)` |
| `g.delete_draft(draft)` | `g.drafts.delete(draft_id)` |

## Agents (Knowledge Agents)

New in guru-py-sdk — no legacy equivalent.

| New |
|-----|
| `g.agents.list()`, `g.agents.get()`, `g.agents.resolve(name)` |
| `g.agents.create(name=, ...)`, `g.agents.update()`, `g.agents.delete()` |
| `g.agents.list_groups()`, `g.agents.add_group()`, `g.agents.remove_group()` |

## Answers

| Legacy | New |
|--------|-----|
| — | `g.answers.ask(question)` |
| — | `g.answers.ask_minimal(question)` |

## Announcements

| Legacy | New |
|--------|-----|
| — | `g.announcements.list()` |
| — | `g.announcements.create(card_id=, group_ids=)` |
| — | `g.announcements.stats(announcement_id)` |

## Pages & Page Drafts

New in guru-py-sdk — no legacy equivalent.

| New |
|-----|
| `g.pages.list()`, `g.pages.get()`, `g.pages.create()`, `g.pages.update()`, `g.pages.delete()` |
| `g.pages.list_nested()`, `g.pages.move()`, `g.pages.list_permissions()` |
| `g.page_drafts.list()`, `g.page_drafts.get()`, `g.page_drafts.create()`, `g.page_drafts.delete()` |

## Data Objects → Pydantic Models + Contrib

Legacy `data_objects` convenience methods are now either on resources or in `guru_sdk.contrib`:

| Legacy | New | Location |
|--------|-----|----------|
| `card.has_text(text)` | `has_text(card.content, text)` | `guru_sdk.contrib` |
| `card.find_urls(func)` | `find_urls(card.content)` | `guru_sdk.contrib` |
| `card.replace_url(old, new)` | `replace_url(card.content, old, new)` | `guru_sdk.contrib` |
| `Bundle(...)` | `Bundle(g)` | `guru_sdk.contrib` |
| `PublisherFolders(...)` | `PublisherFolders(g, ...)` | `guru_sdk.contrib` |

## Removed (Not Migrated)

These legacy methods are intentionally not implemented:

| Legacy | Reason |
|--------|--------|
| All board methods (`get_board`, `make_board`, etc.) | Boards replaced by Folders |
| `upgrade_light_user`, `downgrade_core_user` | Light users no longer exist |
| `util.py` functions (`http_get`, `load_html`, `download_file`, etc.) | Generic helpers; use `httpx`/`pathlib` directly |
