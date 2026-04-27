"""Tests for guru_sdk.contrib.publisher — folder-based content sync framework.

TDD tests covering:
- CardChanges — change detection dataclass
- PublisherFolders — abstract base class for syncing Guru content externally
  - Metadata management (load, save, lookup)
  - publish_collection, publish_folder, publish_card
  - process_deletions
  - dry_run mode
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock

import pytest

from guru_sdk.models._generated import (
    Card,
    CollectionModel,
    Folder,
    FolderItem,
    Tag,
)

if TYPE_CHECKING:
    from pathlib import Path


# =============================================================================
# Test Data
# =============================================================================

CARD_UUID = "c1c1c1c1-c1c1-c1c1-c1c1-c1c1c1c1c1c1"
CARD_UUID_2 = "c2c2c2c2-c2c2-c2c2-c2c2-c2c2c2c2c2c2"
FOLDER_UUID = "f1f1f1f1-f1f1-f1f1-f1f1-f1f1f1f1f1f1"
FOLDER_UUID_2 = "f2f2f2f2-f2f2-f2f2-f2f2-f2f2f2f2f2f2"
COLL_UUID = "d1d1d1d1-d1d1-d1d1-d1d1-d1d1d1d1d1d1"
HOME_FOLDER_UUID = "h1h1h1h1-h1h1-h1h1-h1h1-h1h1h1h1h1h1"


def _make_card(
    card_id: str = CARD_UUID,
    title: str = "Test Card",
    content: str = "<p>Hello</p>",
    verification_state: str = "TRUSTED",
    last_modified: str = "2026-04-13T12:00:00.000+0000",
) -> Card:
    return Card.model_validate(
        {
            "id": card_id,
            "content": content,
            "preferredPhrase": title,
            "verificationState": verification_state,
            "lastModified": last_modified,
        }
    )


def _make_folder(
    folder_id: str = FOLDER_UUID,
    title: str = "Test Folder",
) -> Folder:
    return Folder.model_validate(
        {"id": folder_id, "title": title, "slug": f"slug-{folder_id}", "home": False}
    )


def _make_folder_item(item_id: str, entry_type: str = "folder") -> FolderItem:
    return FolderItem.model_validate(
        {"id": item_id, "itemId": f"placement-{item_id}", "type": entry_type}
    )


def _make_tag(tag_id: str, value: str) -> Tag:
    return Tag.model_validate({"id": tag_id, "value": value})


def _make_guru_mock() -> MagicMock:
    g = MagicMock()
    g.cards = MagicMock()
    g.folders = MagicMock()
    g.collections = MagicMock()
    g.tags = MagicMock()
    return g


# =============================================================================
# Concrete subclass for testing
# =============================================================================


def _make_test_publisher(
    g: MagicMock,
    metadata: dict[str, Any] | None = None,
    dry_run: bool = False,
    metadata_path: Path | None = None,
) -> Any:
    """Create a concrete PublisherFolders subclass for testing."""
    from guru_sdk.contrib.publisher import PublisherFolders

    class TestPublisher(PublisherFolders):
        """Concrete subclass that tracks all hook calls."""

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self.created_cards: list[str] = []
            self.updated_cards: list[str] = []
            self.deleted_cards: list[str] = []
            self.created_folders: list[str] = []
            self.updated_folders: list[str] = []
            self.deleted_folders: list[str] = []
            self.created_collections: list[str] = []
            self.updated_collections: list[str] = []
            self.deleted_collections: list[str] = []

        def create_external_card(
            self, card: Card, changes: Any, folder: Any, collection: Any
        ) -> str | None:
            self.created_cards.append(card.id or "")
            return f"ext-{card.id}"

        def update_external_card(
            self, external_id: str, card: Card, changes: Any, folder: Any, collection: Any
        ) -> bool:
            self.updated_cards.append(external_id)
            return True

        def delete_external_card(self, external_id: str) -> None:
            self.deleted_cards.append(external_id)

        def get_external_url(self, external_id: str | None, card: Card) -> str | None:
            if external_id:
                return f"https://ext.example.com/{external_id}"
            return None

        def create_external_folder(self, folder: Folder, collection: Any) -> str | None:
            self.created_folders.append(folder.id or "")
            return f"ext-folder-{folder.id}"

        def update_external_folder(self, external_id: str, folder: Folder, collection: Any) -> bool:
            self.updated_folders.append(external_id)
            return True

        def delete_external_folder(self, external_id: str) -> None:
            self.deleted_folders.append(external_id)

        def create_external_collection(self, collection: Any) -> str | None:
            self.created_collections.append(collection.id or "")
            return f"ext-coll-{collection.id}"

        def update_external_collection(self, external_id: str, collection: Any) -> bool:
            self.updated_collections.append(external_id)
            return True

        def delete_external_collection(self, external_id: str) -> None:
            self.deleted_collections.append(external_id)

    return TestPublisher(
        g,
        metadata=metadata or {},
        dry_run=dry_run,
        metadata_path=metadata_path,
        silent=True,
    )


# =============================================================================
# CardChanges
# =============================================================================


class TestCardChanges:
    """CardChanges dataclass."""

    def test_needs_publishing_content_changed(self) -> None:
        from guru_sdk.contrib.publisher import CardChanges

        changes = CardChanges(
            content_changed=True,
            folders_added=[],
            folders_removed=[],
            tags_added=[],
            tags_removed=[],
        )
        assert changes.needs_publishing() is True

    def test_needs_publishing_folders_added(self) -> None:
        from guru_sdk.contrib.publisher import CardChanges

        changes = CardChanges(
            content_changed=False,
            folders_added=["New Folder"],
            folders_removed=[],
            tags_added=[],
            tags_removed=[],
        )
        assert changes.needs_publishing() is True

    def test_needs_publishing_tags_changed(self) -> None:
        from guru_sdk.contrib.publisher import CardChanges

        changes = CardChanges(
            content_changed=False,
            folders_added=[],
            folders_removed=[],
            tags_added=["new-tag"],
            tags_removed=[],
        )
        assert changes.needs_publishing() is True

    def test_no_changes_does_not_need_publishing(self) -> None:
        from guru_sdk.contrib.publisher import CardChanges

        changes = CardChanges(
            content_changed=False,
            folders_added=[],
            folders_removed=[],
            tags_added=[],
            tags_removed=[],
        )
        assert changes.needs_publishing() is False

    def test_frozen(self) -> None:
        from guru_sdk.contrib.publisher import CardChanges

        changes = CardChanges(
            content_changed=True,
            folders_added=[],
            folders_removed=[],
            tags_added=[],
            tags_removed=[],
        )
        with pytest.raises(AttributeError):
            changes.content_changed = False  # type: ignore[misc]


# =============================================================================
# Metadata Management
# =============================================================================


class TestMetadata:
    """Metadata load, save, lookup."""

    def test_get_external_id(self) -> None:
        g = _make_guru_mock()
        metadata = {CARD_UUID: {"external_id": "ext-123", "type": "card"}}
        pub = _make_test_publisher(g, metadata=metadata)

        assert pub.get_external_id(CARD_UUID) == "ext-123"

    def test_get_external_id_missing(self) -> None:
        g = _make_guru_mock()
        pub = _make_test_publisher(g)

        assert pub.get_external_id("nonexistent") is None

    def test_get_type(self) -> None:
        g = _make_guru_mock()
        metadata = {CARD_UUID: {"external_id": "ext-123", "type": "card"}}
        pub = _make_test_publisher(g, metadata=metadata)

        assert pub.get_type(CARD_UUID) == "card"

    def test_get_folder_names(self) -> None:
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {
                "external_id": "ext-123",
                "type": "card",
                "folders": ["API Docs", "Getting Started"],
            }
        }
        pub = _make_test_publisher(g, metadata=metadata)

        assert pub.get_folder_names(CARD_UUID) == ["API Docs", "Getting Started"]

    def test_get_tags(self) -> None:
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {
                "external_id": "ext-123",
                "type": "card",
                "tags": ["important", "sdk"],
            }
        }
        pub = _make_test_publisher(g, metadata=metadata)

        assert pub.get_tags(CARD_UUID) == ["important", "sdk"]

    def test_save_metadata(self, tmp_path: Path) -> None:
        g = _make_guru_mock()
        meta_path = tmp_path / "test_meta.json"
        pub = _make_test_publisher(g, metadata_path=meta_path)

        # Trigger a card publish to populate metadata
        card = _make_card()
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []
        pub.publish_card(card, None, None)

        pub.save_metadata()

        # Verify file was written
        assert meta_path.exists()
        saved = json.loads(meta_path.read_text())
        assert CARD_UUID in saved
        assert saved[CARD_UUID]["type"] == "card"

    def test_load_metadata_from_file(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.publisher import PublisherFolders

        meta_path = tmp_path / "existing.json"
        existing = {CARD_UUID: {"external_id": "ext-old", "type": "card"}}
        meta_path.write_text(json.dumps(existing))

        # Create a concrete subclass inline
        class MinimalPublisher(PublisherFolders):
            def create_external_card(self, card, changes, folder, collection):  # type: ignore[override]
                return None

            def update_external_card(self, external_id, card, changes, folder, collection):  # type: ignore[override]
                return True

            def delete_external_card(self, external_id):  # type: ignore[override]
                pass

            def get_external_url(self, external_id, card):  # type: ignore[override]
                return None

        g = _make_guru_mock()
        pub = MinimalPublisher(g, metadata_path=meta_path, silent=True)

        assert pub.get_external_id(CARD_UUID) == "ext-old"


# =============================================================================
# publish_card
# =============================================================================


class TestPublishCard:
    """publish_card — single card sync logic."""

    def test_creates_new_card(self) -> None:
        """Card not in metadata → calls create_external_card."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)
        card = _make_card()
        g.cards.list_folders.return_value = [_make_folder()]
        g.cards.list_tags.return_value = [_make_tag("t1", "sdk")]

        pub.publish_card(card, None, None)

        assert len(pub.created_cards) == 1
        assert CARD_UUID in pub.created_cards

    def test_updates_existing_card(self) -> None:
        """Card in metadata with changes → calls update_external_card."""
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {
                "external_id": "ext-123",
                "type": "card",
                "last_updated": "2026-04-12T00:00:00.000+0000",
                "folders": [],
                "tags": [],
            }
        }
        pub = _make_test_publisher(g, metadata=metadata)
        card = _make_card(last_modified="2026-04-13T12:00:00.000+0000")
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []

        pub.publish_card(card, None, None)

        assert len(pub.updated_cards) == 1
        assert "ext-123" in pub.updated_cards

    def test_skips_unchanged_card(self) -> None:
        """Card in metadata with no changes → skip."""
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {
                "external_id": "ext-123",
                "type": "card",
                "last_updated": "2026-04-13T12:00:00+00:00",
                "folders": ["Test Folder"],
                "tags": ["sdk"],
            }
        }
        pub = _make_test_publisher(g, metadata=metadata)
        card = _make_card(last_modified="2026-04-13T12:00:00.000+0000")
        g.cards.list_folders.return_value = [_make_folder(title="Test Folder")]
        g.cards.list_tags.return_value = [_make_tag("t1", "sdk")]

        pub.publish_card(card, None, None)

        assert len(pub.created_cards) == 0
        assert len(pub.updated_cards) == 0

    def test_skips_unverified_card(self) -> None:
        """Unverified card with skip_unverified=True → skip."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)
        card = _make_card(verification_state="NEEDS_VERIFICATION")

        pub.publish_card(card, None, None)

        assert len(pub.created_cards) == 0

    def test_dry_run_does_not_call_hooks(self) -> None:
        """dry_run=True → no create/update calls, but still tracks results."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g, dry_run=True)
        card = _make_card()
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []

        pub.publish_card(card, None, None)

        assert len(pub.created_cards) == 0
        assert len(pub.updated_cards) == 0


# =============================================================================
# publish_folder
# =============================================================================


class TestPublishFolder:
    """publish_folder — folder sync + recursive traversal."""

    def test_creates_new_folder_and_processes_cards(self) -> None:
        """New folder → create hook, then process contained cards."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)

        folder = _make_folder()
        card = _make_card()

        g.folders.get.return_value = folder
        g.folders.items.return_value = [_make_folder_item(CARD_UUID, "card")]
        g.cards.get.return_value = card
        g.cards.list_folders.return_value = [folder]
        g.cards.list_tags.return_value = []

        pub.publish_folder(FOLDER_UUID)

        assert len(pub.created_folders) == 1
        assert len(pub.created_cards) == 1

    def test_updates_existing_folder(self) -> None:
        """Folder already in metadata → update hook."""
        g = _make_guru_mock()
        metadata = {FOLDER_UUID: {"external_id": "ext-folder-1", "type": "folder"}}
        pub = _make_test_publisher(g, metadata=metadata)

        folder = _make_folder()
        g.folders.get.return_value = folder
        g.folders.items.return_value = []

        pub.publish_folder(FOLDER_UUID)

        assert len(pub.updated_folders) == 1
        assert "ext-folder-1" in pub.updated_folders

    def test_recurses_into_subfolders(self) -> None:
        """Folder containing a subfolder → recursive traversal."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)

        parent_folder = _make_folder(FOLDER_UUID, "Parent")
        child_folder = _make_folder(FOLDER_UUID_2, "Child")

        def get_side_effect(folder_id: str) -> Folder:
            if folder_id == FOLDER_UUID:
                return parent_folder
            return child_folder

        g.folders.get.side_effect = get_side_effect
        g.folders.items.side_effect = [
            [_make_folder_item(FOLDER_UUID_2, "folder")],  # parent's items
            [],  # child's items (empty)
        ]

        pub.publish_folder(FOLDER_UUID)

        assert len(pub.created_folders) == 2

    def test_cards_get_called_with_card_uuid_not_placement_uuid(self) -> None:
        """Regression: cards.get must be called with item.id (card UUID), not item.item_id (placement UUID)."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)

        folder = _make_folder()
        card = _make_card()

        g.folders.get.return_value = folder
        # _make_folder_item sets id=CARD_UUID and itemId="placement-{CARD_UUID}"
        folder_item = _make_folder_item(CARD_UUID, "card")
        g.folders.items.return_value = [folder_item]
        g.cards.get.return_value = card
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []

        pub.publish_folder(FOLDER_UUID)

        # cards.get must be called with the card UUID (item.id), not the placement UUID (item.item_id)
        g.cards.get.assert_called_once_with(CARD_UUID)
        assert folder_item.id == CARD_UUID
        assert folder_item.item_id == f"placement-{CARD_UUID}"


# =============================================================================
# publish_collection
# =============================================================================


class TestPublishCollection:
    """publish_collection — full collection sync."""

    def test_creates_collection_and_processes_home_folder(self) -> None:
        """New collection → create hook, then walk home folder items."""
        g = _make_guru_mock()
        pub = _make_test_publisher(g)

        coll = CollectionModel.model_validate(
            {"id": COLL_UUID, "name": "Engineering", "color": "#4A90D9"}
        )
        home = _make_folder(HOME_FOLDER_UUID, "Home")

        g.collections.get.return_value = coll
        g.collections.home_folder.return_value = home
        g.folders.items.return_value = [_make_folder_item(CARD_UUID, "card")]

        card = _make_card()
        g.cards.get.return_value = card
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []

        pub.publish_collection(COLL_UUID)

        assert len(pub.created_collections) == 1
        assert len(pub.created_cards) == 1


# =============================================================================
# process_deletions
# =============================================================================


class TestProcessDeletions:
    """process_deletions — detect and remove stale items."""

    def test_deletes_cards_not_in_results(self) -> None:
        """Card in metadata but not visited → delete hook called."""
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {"external_id": "ext-old-card", "type": "card"},
            CARD_UUID_2: {"external_id": "ext-kept-card", "type": "card"},
        }
        pub = _make_test_publisher(g, metadata=metadata)

        # Simulate that only CARD_UUID_2 was visited in this run
        card2 = _make_card(card_id=CARD_UUID_2)
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []
        pub.publish_card(card2, None, None)

        pub.process_deletions()

        # CARD_UUID was not visited → should be deleted
        assert "ext-old-card" in pub.deleted_cards
        # CARD_UUID_2 was visited → should NOT be deleted
        assert "ext-kept-card" not in pub.deleted_cards

    def test_deletes_folders(self) -> None:
        """Folder in metadata but not visited → delete hook called."""
        g = _make_guru_mock()
        metadata = {FOLDER_UUID: {"external_id": "ext-old-folder", "type": "folder"}}
        pub = _make_test_publisher(g, metadata=metadata)

        pub.process_deletions()

        assert "ext-old-folder" in pub.deleted_folders

    def test_removes_deleted_items_from_metadata(self) -> None:
        """After deletion, item is removed from metadata."""
        g = _make_guru_mock()
        metadata = {CARD_UUID: {"external_id": "ext-gone", "type": "card"}}
        pub = _make_test_publisher(g, metadata=metadata)

        pub.process_deletions()

        # After deletion, metadata should no longer contain the item
        assert pub.get_external_id(CARD_UUID) is None

    def test_no_deletions_when_all_visited(self) -> None:
        """All metadata items were visited → no deletions."""
        g = _make_guru_mock()
        metadata = {
            CARD_UUID: {
                "external_id": "ext-123",
                "type": "card",
                "last_updated": "2026-04-12T00:00:00.000+0000",
                "folders": [],
                "tags": [],
            }
        }
        pub = _make_test_publisher(g, metadata=metadata)

        # Visit the card
        card = _make_card(last_modified="2026-04-13T12:00:00.000+0000")
        g.cards.list_folders.return_value = []
        g.cards.list_tags.return_value = []
        pub.publish_card(card, None, None)

        pub.process_deletions()

        assert len(pub.deleted_cards) == 0
