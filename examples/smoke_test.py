"""Smoke test — exercises all six core resources against the live API.

Usage:
    export GURU_USER="you@company.com"
    export GURU_TOKEN="your-api-token"
    python examples/smoke_test.py
"""

from guru_sdk import Guru

g = Guru()

# ── Collections ──────────────────────────────────────────────────────────────
print("=== Collections ===")
collections = g.collections.list()
print(f"Found {len(collections)} collections")
for c in collections[:3]:
    print(f"  - {c.name} ({c.id})")

if collections:
    # Get a single collection by name
    first = collections[0]
    by_name = g.collections.get(first.name)
    print(f"\nGet by name '{first.name}': {by_name.id}")

    # Group access
    groups = g.collections.groups(first.id)
    print(f"Groups on '{first.name}': {len(groups)}")
    for grp in groups[:3]:
        print(f"  - {grp.group_name} (role={grp.role})")

    # Home folder
    try:
        home = g.collections.home_folder(first.id)
        print(f"Home folder: {home.title} ({home.id})")
    except Exception as e:
        print(f"Home folder: {e}")

# ── Folders ──────────────────────────────────────────────────────────────────
print("\n=== Folders ===")
if collections:
    folders = g.folders.list(collection_id=collections[0].id)
    print(f"Found {len(folders)} folders in '{collections[0].name}'")
    for f in folders[:5]:
        print(f"  - {f.title} (home={f.home}, id={f.id})")

    if folders:
        # Get folder items
        items = g.folders.items(folders[0].id)
        print(f"\nItems in '{folders[0].title}': {len(items)}")
        for item in items[:5]:
            # Items can be cards or sub-folders — print what we can
            item_title = getattr(item, "title", None) or getattr(item, "preferredPhrase", "?")
            print(f"  - {item_title}")

# ── Cards ────────────────────────────────────────────────────────────────────
print("\n=== Cards ===")
# List unverified cards (a quick way to get some cards without search)
try:
    unverified = g.cards.list_unverified()
    print(f"Unverified cards: {len(unverified)}")
    for card in unverified[:3]:
        print(f"  - {card.preferred_phrase} (id={card.id})")

    if unverified:
        # Get a single card
        card = g.cards.get(unverified[0].id)
        print(f"\nCard detail: {card.preferred_phrase}")
        print(f"  Collection: {card.collection}")
        print(f"  Verified: {card.verification_state}")

        # List tags on the card
        tags = g.cards.list_tags(card.id)
        print(f"  Tags: {[t.value for t in tags] if tags else 'none'}")

        # List comments
        comments = g.cards.list_comments(card.id)
        print(f"  Comments: {len(comments)}")
except Exception as e:
    print(f"Cards error: {e}")

# ── Groups ──────────────────────────────────────────────────────────────────
print("\n=== Groups ===")
try:
    all_groups = g.groups.list()
    print(f"Found {len(all_groups)} groups")
    for grp in all_groups[:5]:
        print(f"  - {grp.name} (id={grp.id}, members={grp.number_of_members})")

    if all_groups:
        # Get group members
        first_group = all_groups[0]
        members = g.groups.members(first_group.id)
        print(f"\nMembers of '{first_group.name}': {len(members)}")
        for m in members[:3]:
            print(f"  - {m.user.email} ({m.user.first_name} {m.user.last_name})")
except Exception as e:
    print(f"Groups error: {e}")

# ── Members ─────────────────────────────────────────────────────────────────
print("\n=== Members ===")
try:
    all_members = g.members.list()
    print(f"Found {len(all_members)} members")
    for m in all_members[:3]:
        print(f"  - {m.user.email} ({m.user.first_name} {m.user.last_name})")
except Exception as e:
    print(f"Members error: {e}")

# ── Tags ────────────────────────────────────────────────────────────────────
print("\n=== Tags ===")
try:
    categories = g.tags.list_categories()
    print(f"Found {len(categories)} tag categories")
    for cat in categories:
        tag_count = len(cat.tags) if cat.tags else 0
        print(f"  - {cat.name} ({tag_count} tags)")
        if cat.tags:
            for t in cat.tags[:3]:
                print(f"      • {t.value}")
except Exception as e:
    print(f"Tags error: {e}")

print("\n✓ Smoke test complete")
