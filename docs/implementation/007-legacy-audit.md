# Iteration 007 — Legacy Guru Class Audit

**Date**: 2026-04-10
**Status**: Complete

## Goal

Systematic audit of every public method on py-sdk's `Guru` class and supporting modules. Categorize each as covered, future resource, contrib candidate, utility, or deprecated. Produce a migration matrix that informs Phase 3, Phase 4, and the contrib backlog.

## Migration Matrix — Guru Class Methods (110+ methods)

### Legend

| Category | Meaning |
|----------|---------|
| **✅ Covered** | Already implemented in guru-py-sdk |
| **📦 Phase 3** | Belongs on a resource not yet built |
| **🔧 Contrib** | Convenience workflow — composes multiple API calls |
| **🛠 Utility** | Local helper (content parsing, file I/O, etc.) |
| **❌ Deprecated** | Board operations or obsolete — do not implement |

---

### Cards (15 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_card(card)` | ✅ Covered | `g.cards.get()` | |
| `get_cards(card_ids)` | ✅ Covered | `g.cards.get_bulk()` | |
| `get_visible_cards()` | 📦 Phase 3 | — | Needs search resource |
| `get_card_version(card, version)` | ✅ Covered | `g.cards.get_version()` | |
| `make_card(title, content, collection)` | ✅ Covered | `g.cards.create()` | |
| `find_card(**kwargs)` | 📦 Phase 3 | — | Needs search resource |
| `find_cards(...)` | 📦 Phase 3 | — | Needs search resource (cardmgr endpoint) |
| `upload_file(filename)` | 📦 Phase 3 | — | Attachment upload |
| `patch_card(card)` | ✅ Covered | `g.cards.patch()` | |
| `save_card(card, verify)` | ✅ Covered | `g.cards.update()` | py-sdk also verifies if flag set |
| `verify_card(card)` | ✅ Covered | `g.cards.verify()` | |
| `unverify_card(card)` | ✅ Covered | `g.cards.unverify()` | |
| `archive_card(card)` | ✅ Covered | `g.cards.archive()` | |
| `restore_card(card)` | ✅ Covered | `g.cards.restore()` | |
| `restore_cards(*card_ids, timeout)` | 🔧 Contrib | — | Bulk restore with polling — convenience workflow |

### Card Favorites (3 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_favorite_lists()` | ✅ Covered | — | Needed for `favorite()` — currently raises NotImplementedError |
| `favorite_card(card)` | ✅ Covered | `g.cards.favorite()` | Raises NotImplementedError (needs favorite list API) |
| `unfavorite_card(card)` | ✅ Covered | `g.cards.unfavorite()` | |

### Card Comments (6 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `add_comment_to_card(card, comment)` | ✅ Covered | `g.cards.add_comment()` | |
| `get_card_comments(card, status)` | ✅ Covered | `g.cards.list_comments()` | |
| `update_card_comment(comment)` | ✅ Covered | `g.cards.update_comment()` | |
| `resolve_card_comment(comment)` | ✅ Covered | `g.cards.resolve_comment()` | |
| `reopen_card_comment(comment)` | ✅ Covered | `g.cards.unresolve_comment()` | |
| `delete_card_comment(card, comment_id)` | ✅ Covered | `g.cards.delete_comment()` | |

### Card PDF (1 method)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `download_card_as_pdf(card, filename)` | ✅ Covered | `g.cards.download_pdf()` | SDK returns bytes; file write is caller's responsibility |

### Drafts (3 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_drafts(card)` | 📦 Phase 3 | — | DraftResource (iteration 010) |
| `create_draft(title, content)` | 📦 Phase 3 | — | DraftResource |
| `delete_draft(draft)` | 📦 Phase 3 | — | DraftResource |

### Collections (8 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_collection(collection)` | ✅ Covered | `g.collections.get()` | |
| `get_collections()` | ✅ Covered | `g.collections.list()` | |
| `make_collection(name, ...)` | ✅ Covered | `g.collections.create()` | py-sdk also adds group access + framework in one call |
| `delete_collection(collection)` | ✅ Covered | `g.collections.remove()` | |
| `get_groups_on_collection(collection)` | ✅ Covered | `g.collections.groups()` | |
| `add_group_to_collection(group, collection, role)` | ✅ Covered | `g.collections.add_group()` | py-sdk also handles update-if-exists |
| `remove_group_from_collection(group, collection)` | ✅ Covered | `g.collections.remove_group()` | |
| `upload_content(collection, filename, zip)` | 🔧 Contrib | — | Zip upload for content sync |

### Groups (5 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_group(group)` | ✅ Covered | `g.groups.get()` | |
| `get_groups()` | ✅ Covered | `g.groups.list()` | |
| `make_group(name)` | ✅ Covered | `g.groups.create()` | py-sdk checks for duplicate names |
| `delete_group(group)` | ✅ Covered | `g.groups.remove()` | |
| `get_group_members(group)` | ✅ Covered | `g.groups.members()` | |

### Members / Users (11 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_members(search)` | ✅ Covered | `g.members.list(search=)` | |
| `invite_user(email, *groups)` | ✅ Covered | `g.members.invite()` | py-sdk also adds to groups |
| `invite_light_user(email)` | ✅ Covered | `g.members.invite(member_type="LIGHT")` | |
| `invite_core_user(email, *groups)` | ✅ Covered | `g.members.invite()` | |
| `upgrade_light_user(email)` | ❌ Deprecated | — | Light users no longer exist |
| `downgrade_core_user(email)` | ❌ Deprecated | — | Light users no longer exist |
| `add_users_to_group(emails, group)` | 🔧 Contrib | — | Batch with retry (100 per batch) |
| `add_user_to_groups(email, *groups)` | 🔧 Contrib | — | Multi-group convenience |
| `add_user_to_group(email, group)` | ✅ Covered | `g.groups.add_members()` | |
| `remove_user_from_groups(email, *groups)` | 🔧 Contrib | — | Multi-group convenience |
| `remove_user_from_group(email, group)` | ✅ Covered | `g.groups.remove_member()` | |
| `remove_user_from_team(email)` | ✅ Covered | `g.members.remove()` | py-sdk uses `/replaceverifier` endpoint |

### Tags (12 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_tag(tag)` | ✅ Covered | `g.tags.get_tag()` | |
| `get_tags()` | ✅ Covered | `g.tags.list_categories()` | Flattened in py-sdk; categories in new SDK |
| `get_tag_category_id(category)` | 🛠 Utility | — | Simple lookup; user can do `cat.id` |
| `get_tag_category(category)` | 🛠 Utility | — | Simple lookup from `list_categories()` |
| `get_tag_categories()` | ✅ Covered | `g.tags.list_categories()` | |
| `get_tag_category_names()` | 🛠 Utility | — | `[c.name for c in g.tags.list_categories()]` |
| `get_team_id()` | ✅ Covered | Internal in TagResource | Cached via `_get_team_id()` |
| `make_tag(tag)` | ✅ Covered | `g.tags.create_tag()` | |
| `delete_tag(tag)` | 📦 Phase 3 | — | Uses bulk operations |
| `merge_tags(*tags)` | 📦 Phase 3 | — | Uses bulk operations |
| `add_tag_to_card(tag, card, create)` | ✅ Covered | `g.cards.add_tag()` | py-sdk auto-creates tag if `create=True` |
| `remove_tag_from_card(tag, card)` | ✅ Covered | `g.cards.remove_tag()` | |

### Folders (16 methods)

| py-sdk Method | Category | guru-py-sdk Equivalent | Notes |
|---------------|----------|----------------------|-------|
| `get_folder(folder)` | ✅ Covered | `g.folders.get()` | |
| `get_folder_items(folder_id)` | ✅ Covered | `g.folders.items()` | |
| `get_folders(collection)` | ✅ Covered | `g.folders.list()` | |
| `delete_folder(folder, remove_type)` | ✅ Covered | `g.folders.remove()` | |
| `add_folder(title, collection, parent)` | ✅ Covered | `g.folders.create()` | |
| `remove_card_from_folder(card, folder)` | ✅ Covered | `g.cards.remove_from_folder()` | On CardResource |
| `add_card_to_folder(card, folder)` | ✅ Covered | `g.cards.add_to_folder()` | On CardResource |
| `get_folders_for_card(card)` | ✅ Covered | `g.cards.list_folders()` | On CardResource |
| `get_parent_folder(folder)` | ✅ Covered | `g.folders.parent()` | |
| `get_home_folder(collection)` | ✅ Covered | `g.collections.home_folder()` | On CollectionResource |
| `get_shared_folder_groups(folder)` | ✅ Covered | `g.folders.permissions()` | |
| `add_shared_folder_group(folder, group)` | ✅ Covered | `g.folders.add_permission()` | |
| `remove_shared_folder_group(folder, group)` | ✅ Covered | `g.folders.remove_permission()` | |
| `move_folder_to_collection(folder, collection)` | ✅ Covered | `g.folders.move_to_collection()` | |
| `move_card_to_folder(card, src, dst)` | 🔧 Contrib | — | Remove from src + add to dst (two API calls) |
| `move_folder_to_folder(src, dst)` | 🔧 Contrib | — | Uses `/folders/{slug}/action` |
| `set_item_save_folder(folder)` | 🔧 Contrib | — | Uses `/folders/{slug}/action` with MOVE |
| `move_card_to_collection(card, collection)` | ✅ Covered | `g.cards.move_to_collection()` | On CardResource |

### Boards (10+ methods) — ALL DEPRECATED

| py-sdk Method | Category | Notes |
|---------------|----------|-------|
| `get_board`, `get_boards`, `make_board`, `save_board` | ❌ Deprecated | Boards replaced by folders |
| `add_card_to_board`, `remove_card_from_board` | ❌ Deprecated | |
| `add_section_to_board`, `delete_board` | ❌ Deprecated | |
| `set_item_order` | ❌ Deprecated | |
| `get_board_group`, `make_board_group`, `add_board_to_board_group` | ❌ Deprecated | |
| `get_home_board` | ❌ Deprecated | |
| `get_shared_groups`, `add_shared_group`, `remove_shared_group` | ❌ Deprecated | Board sharing |
| `move_board_to_collection` | ❌ Deprecated | |

### Frameworks (3 methods)

| py-sdk Method | Category | Notes |
|---------------|----------|-------|
| `get_frameworks()` | 📦 Phase 3 | Low priority — verification frameworks |
| `get_framework(framework)` | 📦 Phase 3 | |
| `import_framework(framework)` | 📦 Phase 3 | |

### Questions (4 methods)

| py-sdk Method | Category | Notes |
|---------------|----------|-------|
| `get_questions(type)` | 📦 Phase 3 | AnswerResource (iteration 012) |
| `get_questions_inbox()` | 📦 Phase 3 | |
| `get_questions_sent()` | 📦 Phase 3 | |
| `delete_question(question)` | 📦 Phase 3 | |

### Misc / Team (5 methods)

| py-sdk Method | Category | Notes |
|---------------|----------|-------|
| `get_events(start, end)` | 📦 Phase 3 | Event/analytics resource |
| `get_team_stats()` | 📦 Phase 3 | Team resource or analytics |
| `get_reviewed_answers()` | 📦 Phase 3 | AnswerResource |
| `delete_knowledge_trigger(trigger_id)` | 📦 Phase 3 | Knowledge trigger resource |
| `bundle(...)` / `sync(...)` | 🔧 Contrib | Delegates to Bundle class — Phase 4 |

---

## Supporting Modules

### data_objects.py (22 classes)

All replaced by Pydantic models in `models/_generated.py`. The py-sdk classes include convenience methods (e.g., `Card.has_text()`, `Folder.items()`, `Board.add_card()`) that are either:
- Now on resource classes (CRUD operations)
- Candidates for contrib utilities (content parsing)
- Deprecated (board operations)

Key convenience methods to consider for contrib:

| Method | Class | Category | Notes |
|--------|-------|----------|-------|
| `Card.has_text(text)` | Card | 🔧 Contrib | Content search utility |
| `Card.find_urls(func)` | Card | 🔧 Contrib | URL extraction from HTML |
| `Card.replace_url(old, new)` | Card | 🔧 Contrib | URL rewriting in card HTML |
| `Card.download_resources()` | Card | 🔧 Contrib | Downloads images/attachments from card HTML |
| `find_urls_in_doc(doc)` | standalone | 🔧 Contrib | HTML URL extraction |

### util.py (16 functions)

General-purpose helpers, mostly for file I/O and HTTP. Not SDK-specific. Categories:

| Function | Category | Notes |
|----------|----------|-------|
| `load_html`, `http_get`, `http_post` | 🛠 Utility | Generic HTTP; users should use httpx directly |
| `download_file` | 🛠 Utility | Generic; not SDK concern |
| `make_dir`, `clear_dir`, `write_file`, `read_file`, `copy_file` | 🛠 Utility | File I/O; use pathlib |
| `to_yaml`, `load_json`, `save_json` | 🛠 Utility | Serialization; standard library |
| `find_by_name_or_id`, `find_by_email`, `find_by_id` | 🛠 Utility | Replaced by name resolution in resources |
| `format_timestamp`, `compare_datetime_string` | 🛠 Utility | Date helpers; not SDK concern |
| `clean_slug` | 🛠 Utility | Internal; used by folder operations |

### publish.py / publish_folders.py

| Class | Category | Notes |
|-------|----------|-------|
| `Publisher` (35 methods) | 🔧 Contrib | Phase 4, iteration 014 — board-based publishing (deprecated) |
| `PublisherFolders` (25 methods) | 🔧 Contrib | Phase 4, iteration 014 — folder-based publishing |

### bundle.py

| Class | Category | Notes |
|-------|----------|-------|
| `Bundle` (17 methods) | 🔧 Contrib | Phase 4, iteration 015 — bulk export/import |
| `BundleNode` | 🔧 Contrib | Tree node for bundle structure |

---

## Summary Statistics

| Category | Count | % |
|----------|-------|---|
| ✅ Covered | ~55 | 50% |
| 📦 Phase 3 (future resource) | ~18 | 16% |
| 🔧 Contrib (convenience workflow) | ~15 | 14% |
| 🛠 Utility (not SDK concern) | ~10 | 9% |
| ❌ Deprecated (boards) | ~12 | 11% |

**Key takeaway**: Phase 2 covers half of all py-sdk functionality. The remaining gaps are split between future resources (search, drafts, answers — already on the backlog), contrib workflows (multi-step operations), and board operations that shouldn't be implemented.

## Contrib Backlog (from this audit)

These are the convenience workflows identified for `contrib/`:

1. **Card content utilities** — `has_text()`, `find_urls()`, `replace_url()`, `download_resources()`
2. **Move card between folders** — remove from source + add to destination
3. **Move folder to folder** — uses `/folders/{slug}/action`
4. **Batch add users to group** — 100-per-batch with retry
5. **Add user to multiple groups** — loop + error collection
6. **Remove user from multiple groups** — loop + error collection
7. **Bulk restore cards** — with async polling
8. **Upload content to collection** — zip-based content sync
9. **Make collection with full setup** — create + add group + set framework
10. **Add tag to card with auto-create** — create tag if missing, then add
11. **PublisherFolders** — folder-based content publishing
12. **Bundle** — bulk export/import
