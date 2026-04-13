"""Folder-based content sync framework — publish Guru content to external systems.

An abstract base class that walks a Guru collection's folder hierarchy,
detects changes since the last publish via a local metadata file, and calls
abstract hooks that subclasses implement for their target system.

Usage::

    from guru_sdk import Guru
    from guru_sdk.contrib.publisher import PublisherFolders

    class ReadmePublisher(PublisherFolders):
        def create_external_card(self, card, changes, folder, collection):
            # POST to readme.io API
            return readme_doc_slug

        def update_external_card(self, external_id, card, changes, folder, collection):
            # PUT to readme.io API
            return True

        def delete_external_card(self, external_id):
            # DELETE from readme.io API
            pass

        def get_external_url(self, external_id, card):
            return f"https://docs.example.com/{external_id}"

    g = Guru()
    pub = ReadmePublisher(g, metadata_path="readme_sync.json")
    pub.publish_collection("Engineering")
    pub.process_deletions()
    pub.save_metadata()
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from guru_sdk.client import Guru
    from guru_sdk.models._generated import Card, CollectionModel, Folder


# =============================================================================
# CardChanges — change detection dataclass
# =============================================================================


@dataclass(frozen=True)
class CardChanges:
    """Tracks what changed on a card since the last publish.

    Used by publish_card to decide whether to create/update and to pass
    change context to the subclass hooks.
    """

    content_changed: bool
    folders_added: list[str]
    folders_removed: list[str]
    tags_added: list[str]
    tags_removed: list[str]

    def needs_publishing(self) -> bool:
        """Return True if any field indicates a change worth publishing."""
        return bool(
            self.content_changed
            or self.folders_added
            or self.folders_removed
            or self.tags_added
            or self.tags_removed
        )


# =============================================================================
# PublisherFolders — abstract base class
# =============================================================================


class PublisherFolders(ABC):
    """Abstract base class for syncing Guru content to an external system.

    Subclasses implement the abstract hooks (create/update/delete for cards,
    optionally for folders and collections). The base class handles:
    - Recursive traversal of the Guru folder hierarchy
    - Change detection via metadata comparison
    - Metadata persistence (JSON file)
    - Dry-run mode
    - Logging

    Args:
        g: Guru client instance.
        metadata: Pre-loaded metadata dict. If None, loads from metadata_path.
        metadata_path: Path to the metadata JSON file. Defaults to "publisher.json".
        dry_run: If True, detect changes but don't call external hooks.
        skip_unverified_cards: If True, skip cards not in TRUSTED state.
        silent: If True, suppress log output.
    """

    def __init__(
        self,
        g: Guru,
        *,
        metadata: dict[str, Any] | None = None,
        metadata_path: Path | str | None = None,
        dry_run: bool = False,
        skip_unverified_cards: bool = True,
        silent: bool = False,
    ) -> None:
        self._g = g
        self._dry_run = dry_run
        self._skip_unverified_cards = skip_unverified_cards
        self._silent = silent
        self._metadata_path = Path(metadata_path) if metadata_path else Path("publisher.json")

        # Load metadata from argument or file
        if metadata is not None:
            self._metadata: dict[str, Any] = metadata
        elif self._metadata_path.exists():
            self._metadata = json.loads(self._metadata_path.read_text(encoding="utf-8"))
        else:
            self._metadata = {}

        # Track which Guru IDs were visited in this publish run
        self._results: dict[str, str] = {}
        # Log messages
        self.messages: list[dict[str, str]] = []

    # -------------------------------------------------------------------------
    # Abstract Hooks — subclasses MUST implement these
    # -------------------------------------------------------------------------

    @abstractmethod
    def create_external_card(
        self,
        card: Card,
        changes: CardChanges,
        folder: Folder | None,
        collection: CollectionModel | None,
    ) -> str | None:
        """Create a card in the external system.

        Returns:
            The external system's ID for this card, or None on failure.
        """

    @abstractmethod
    def update_external_card(
        self,
        external_id: str,
        card: Card,
        changes: CardChanges,
        folder: Folder | None,
        collection: CollectionModel | None,
    ) -> bool:
        """Update an existing card in the external system.

        Returns:
            True if the update was successful.
        """

    @abstractmethod
    def delete_external_card(self, external_id: str) -> None:
        """Delete a card from the external system."""

    @abstractmethod
    def get_external_url(self, external_id: str | None, card: Card) -> str | None:
        """Convert an external ID to a URL for cross-card link rewriting."""

    # -------------------------------------------------------------------------
    # Optional Hooks — subclasses MAY override these
    # -------------------------------------------------------------------------

    def find_external_card(self, card: Card) -> str | None:
        """Try to find a pre-existing external card (e.g., by title match)."""
        return None

    def find_external_folder(self, folder: Folder) -> str | None:
        """Try to find a pre-existing external folder (e.g., by name match)."""
        return None

    def find_external_collection(self, collection: CollectionModel) -> str | None:
        """Try to find a pre-existing external collection."""
        return None

    def create_external_folder(
        self, folder: Folder, collection: CollectionModel | None
    ) -> str | None:
        """Create a folder in the external system. Returns external_id or None."""
        return None

    def update_external_folder(
        self, external_id: str, folder: Folder, collection: CollectionModel | None
    ) -> bool:
        """Update an existing folder in the external system."""
        return False

    def delete_external_folder(self, external_id: str) -> None:  # noqa: B027
        """Delete a folder from the external system."""

    def create_external_collection(self, collection: CollectionModel) -> str | None:
        """Create a collection in the external system. Returns external_id or None."""
        return None

    def update_external_collection(
        self, external_id: str, collection: CollectionModel
    ) -> bool:
        """Update an existing collection in the external system."""
        return False

    def delete_external_collection(self, external_id: str) -> None:  # noqa: B027
        """Delete a collection from the external system."""

    # -------------------------------------------------------------------------
    # Public API — Publishing
    # -------------------------------------------------------------------------

    def publish_collection(self, collection_id: str) -> None:
        """Walk an entire collection and sync all items.

        Creates/updates the collection itself, then recursively processes
        all folders and cards in the home folder.
        """
        collection = self._g.collections.get(collection_id)
        home_folder = self._g.collections.home_folder(collection_id)

        # Sync the collection object itself
        external_id = self.get_external_id(collection.id or "")
        if not external_id:
            self._log("find collection", collection.name or "")
            external_id = self.find_external_collection(collection)
            if external_id:
                self._log("found collection!", collection.name or "", "->", external_id)

        successful = False
        coll_id = collection.id or ""
        if external_id:
            self._results[coll_id] = "update"
            self._log("update collection", external_id, collection.name or "")
            if not self._dry_run:
                result = self.update_external_collection(external_id, collection)
                successful = bool(result)
        else:
            self._results[coll_id] = "create"
            self._log("create collection", collection.name or "")
            if not self._dry_run:
                external_id = self.create_external_collection(collection)
                successful = external_id is not None

        if successful or external_id:
            self._update_metadata(coll_id, external_id=external_id or "", obj_type="collection")

        # Walk the home folder's items
        self._process_folder_items(home_folder.id or "", collection, home_folder)

    def publish_folder(
        self,
        folder_id: str,
        collection: CollectionModel | None = None,
    ) -> None:
        """Sync a folder and recursively process its contents."""
        folder = self._g.folders.get(folder_id)

        # Sync the folder object itself
        external_id = self.get_external_id(folder.id or "")
        if not external_id:
            self._log("find folder", folder.title or "")
            external_id = self.find_external_folder(folder)
            if external_id:
                self._log("found folder!", folder.title or "", "->", external_id)

        successful = False
        f_id = folder.id or ""
        if external_id:
            self._results[f_id] = "update"
            self._log("update folder", external_id, folder.title or "")
            if not self._dry_run:
                result = self.update_external_folder(external_id, folder, collection)
                successful = bool(result)
        else:
            self._results[f_id] = "create"
            self._log("create folder", folder.title or "")
            if not self._dry_run:
                external_id = self.create_external_folder(folder, collection)
                successful = external_id is not None

        if successful or external_id:
            self._update_metadata(f_id, external_id=external_id or "", obj_type="folder")

        # Walk this folder's items
        self._process_folder_items(f_id, collection, folder)

    def publish_card(
        self,
        card: Card,
        collection: CollectionModel | None,
        folder: Folder | None,
    ) -> None:
        """Sync a single card — detect changes and call create/update hook."""
        card_id = card.id or ""

        # Skip unverified cards if configured
        if self._skip_unverified_cards:
            vs = card.verification_state
            if vs is not None and vs.value != "TRUSTED":
                self._results[card_id] = "skip"
                self._log("skip card (unverified)", card.preferred_phrase)
                return

        # Detect changes
        changes = self.get_card_changes(card)
        if not changes.needs_publishing():
            self._results[card_id] = "skip"
            self._log("skip card (no changes)", card.preferred_phrase)
            return

        # Look up existing external ID
        external_id = self.get_external_id(card_id)
        if not external_id:
            self._log("find card", card.preferred_phrase)
            external_id = self.find_external_card(card)
            if external_id:
                self._log("found card!", card.preferred_phrase, "->", external_id)

        # Create or update
        successful = False
        if external_id:
            self._results[card_id] = "update"
            self._log("update card", external_id, card.preferred_phrase)
            if not self._dry_run:
                result = self.update_external_card(
                    external_id, card, changes, folder, collection
                )
                successful = bool(result)
        else:
            self._results[card_id] = "create"
            self._log("create card", card.preferred_phrase)
            if not self._dry_run:
                external_id = self.create_external_card(card, changes, folder, collection)
                successful = external_id is not None

        # Update metadata
        if successful:
            # Fetch current folder/tag assignments for metadata tracking
            folders = self._g.cards.list_folders(card_id)
            tags = self._g.cards.list_tags(card_id)
            self._update_metadata(
                card_id,
                external_id=external_id or "",
                obj_type="card",
                last_updated=card.last_modified.isoformat() if card.last_modified else None,
                folders=[f.title or "" for f in folders],
                tags=[t.value or "" for t in tags],
            )
        elif external_id:
            self._update_metadata(card_id, external_id=external_id, obj_type="card")

    def process_deletions(self) -> None:
        """Find items in metadata that weren't visited and delete them externally.

        Call this after publish_collection to clean up items that were
        removed from Guru since the last run.
        """
        for guru_id in list(self._metadata.keys()):
            if guru_id not in self._results:
                obj_type = self.get_type(guru_id)
                external_id = self.get_external_id(guru_id)

                if external_id:
                    if obj_type == "card":
                        self.delete_external_card(external_id)
                    elif obj_type == "folder":
                        self.delete_external_folder(external_id)
                    elif obj_type == "collection":
                        self.delete_external_collection(external_id)

                # Remove from metadata so re-creation is treated as new
                del self._metadata[guru_id]

    # -------------------------------------------------------------------------
    # Public API — Metadata Queries
    # -------------------------------------------------------------------------

    def get_external_id(self, guru_id: str) -> str | None:
        """Look up the external system ID for a Guru object."""
        val: object = self._metadata.get(guru_id, {}).get("external_id")
        return str(val) if val is not None else None

    def get_type(self, guru_id: str) -> str | None:
        """Look up the object type (card, folder, collection) from metadata."""
        val: object = self._metadata.get(guru_id, {}).get("type")
        return str(val) if val is not None else None

    def get_folder_names(self, guru_id: str) -> list[str]:
        """Look up the folder names a card was assigned to at last publish."""
        return self._metadata.get(guru_id, {}).get("folders") or []

    def get_tags(self, guru_id: str) -> list[str]:
        """Look up the tag values a card had at last publish."""
        return self._metadata.get(guru_id, {}).get("tags") or []

    def get_last_updated(self, guru_id: str) -> str | None:
        """Look up the last-published timestamp for a Guru object."""
        val: object = self._metadata.get(guru_id, {}).get("last_updated")
        return str(val) if val is not None else None

    def get_card_changes(self, card: Card) -> CardChanges:
        """Compute what changed on a card since the last publish.

        Compares the card's current state against stored metadata to detect
        content changes, folder reassignments, and tag changes.
        """
        card_id = card.id or ""

        # Content change: compare timestamps using ISO format for consistency
        content_changed = False
        last_published = self.get_last_updated(card_id)
        current_ts = card.last_modified.isoformat() if card.last_modified else None
        if not last_published or current_ts != last_published:
            content_changed = True

        # Folder changes: compare current assignments against stored
        old_folders = set(self.get_folder_names(card_id))
        current_folders_raw = self._g.cards.list_folders(card_id)
        new_folders = {f.title or "" for f in current_folders_raw}
        folders_added = list(new_folders - old_folders)
        folders_removed = list(old_folders - new_folders)

        # Tag changes: compare current tags against stored
        old_tags = set(self.get_tags(card_id))
        current_tags_raw = self._g.cards.list_tags(card_id)
        new_tags = {t.value or "" for t in current_tags_raw}
        tags_added = list(new_tags - old_tags)
        tags_removed = list(old_tags - new_tags)

        return CardChanges(
            content_changed=content_changed,
            folders_added=folders_added,
            folders_removed=folders_removed,
            tags_added=tags_added,
            tags_removed=tags_removed,
        )

    # -------------------------------------------------------------------------
    # Public API — Persistence
    # -------------------------------------------------------------------------

    def save_metadata(self) -> None:
        """Write the current metadata to disk."""
        self._metadata_path.write_text(
            json.dumps(self._metadata, indent=2, default=str),
            encoding="utf-8",
        )

    # -------------------------------------------------------------------------
    # Logging
    # -------------------------------------------------------------------------

    def log(self, message: str) -> None:
        """Log an info message."""
        if not self._silent:
            print("LOG:", message)
        self.messages.append({"type": "info", "message": message})

    def log_error(self, message: str) -> None:
        """Log an error message."""
        if not self._silent:
            print("ERROR:", message)
        self.messages.append({"type": "error", "message": message})

    # -------------------------------------------------------------------------
    # Private — Traversal
    # -------------------------------------------------------------------------

    def _process_folder_items(
        self,
        folder_id: str,
        collection: CollectionModel | None,
        folder: Folder | None,
    ) -> None:
        """Walk a folder's items, dispatching folders and cards."""
        from guru_sdk.models._generated import Type9

        items = self._g.folders.items(folder_id)

        for item in items:
            if item.type == Type9.folder and item.item_id:
                self.publish_folder(item.item_id, collection)
            elif item.type == Type9.card and item.item_id:
                card = self._g.cards.get(item.item_id)
                self.publish_card(card, collection, folder)

    # -------------------------------------------------------------------------
    # Private — Metadata Updates
    # -------------------------------------------------------------------------

    def _update_metadata(
        self,
        guru_id: str,
        *,
        external_id: str = "",
        obj_type: str = "",
        last_updated: str | None = None,
        folders: list[str] | None = None,
        tags: list[str] | None = None,
    ) -> None:
        """Update metadata for a Guru object."""
        if guru_id not in self._metadata:
            self._metadata[guru_id] = {}

        entry = self._metadata[guru_id]

        if external_id:
            entry["external_id"] = external_id
        if obj_type:
            entry["type"] = obj_type
        if last_updated is not None:
            entry["last_updated"] = last_updated
        if folders is not None:
            entry["folders"] = folders
        if tags is not None:
            entry["tags"] = tags

    def _log(self, *args: Any) -> None:
        """Internal log helper — joins args into a message string."""
        message = " ".join(str(a) for a in args)
        if not self._silent:
            print(message)
