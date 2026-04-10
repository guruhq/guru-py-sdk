"""Folder resource — CRUD, hierarchy, permissions, cross-collection move.

Folders organize cards within collections. Each collection has a home folder
that serves as the root. Folders support nested hierarchies, item listing,
and folder-level permission overrides.

API surface mirrors guru-cli's FolderResource — same vocabulary, same
endpoint paths.
"""

from __future__ import annotations

from typing import Any

from guru_sdk._compat import is_uuid, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models import (
    EffectivePermissions,
    Folder,
    FolderItem,
)
from guru_sdk.models._generated import UserGroupAccess
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — FolderResource
# =============================================================================


class FolderResource(BaseResource):
    """Guru Folders — CRUD, hierarchy traversal, permissions, cross-collection move.

    All methods accept either a folder UUID or a folder title. When a title
    is passed, it resolves to a UUID via name resolution.
    """

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    def get(self, folder_id: str) -> Folder:
        """Get a single folder by ID or title.

        Args:
            folder_id: Folder UUID or exact title (case-insensitive).
        """
        resolved = self._resolve_folder(folder_id)
        return self._http.get(f"/folders/{resolved}", Folder)

    def list(self, *, collection_id: str | None = None) -> list[Folder]:
        """List all accessible folders.

        Args:
            collection_id: Optional collection UUID to filter by.
        """
        if collection_id is not None:
            validate_input(collection_id, "collection_id")
            return self._http.get_list(
                "/folders", Folder, collection=collection_id
            )
        return self._http.get_list("/folders", Folder)

    def create(
        self,
        *,
        title: str,
        collection_id: str,
        description: str | None = None,
    ) -> Folder:
        """Create a new folder in a collection.

        Args:
            title: Folder title.
            collection_id: UUID of the collection to create the folder in.
            description: Optional folder description.
        """
        validate_input(title, "title")
        validate_input(collection_id, "collection_id")

        body: dict[str, Any] = {
            "title": title,
            "collection": {"id": collection_id},
        }
        if description is not None:
            body["description"] = description

        return self._http.post("/folders", body, Folder)

    def update(
        self,
        folder_id: str,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> Folder:
        """Update an existing folder.

        Only the provided fields are sent — omitted fields are left unchanged.

        Args:
            folder_id: Folder UUID or title.
            title: New title (optional).
            description: New description (optional).
        """
        resolved = self._resolve_folder(folder_id)

        body: dict[str, Any] = {}
        if title is not None:
            validate_input(title, "title")
            body["title"] = title
        if description is not None:
            body["description"] = description

        return self._http.put(f"/folders/{resolved}", body, Folder)

    def remove(
        self,
        folder_id: str,
        *,
        remove_type: str | None = None,
    ) -> None:
        """Delete a folder.

        Args:
            folder_id: Folder UUID or title.
            remove_type: Controls what happens to child content:
                - None (default): server default behavior
                - "FOLDERS_ONLY": delete folder, keep cards in parent
                - "FOLDERS_AND_CARDS": delete folder and all cards
                - "PROMOTE_TO_PARENT": move cards to parent folder
        """
        resolved = self._resolve_folder(folder_id)
        if remove_type is not None:
            self._http.delete(f"/folders/{resolved}", removeType=remove_type)
        else:
            self._http.delete(f"/folders/{resolved}")

    # -------------------------------------------------------------------------
    # Hierarchy
    # -------------------------------------------------------------------------

    def items(self, folder_id: str) -> list[FolderItem]:
        """List items (cards, sub-folders) in a folder.

        Args:
            folder_id: Folder UUID or title.
        """
        resolved = self._resolve_folder(folder_id)
        return self._http.get_list(f"/folders/{resolved}/items", FolderItem)

    def parent(self, folder_id: str) -> Folder:
        """Get the parent folder.

        Args:
            folder_id: Folder UUID or title.
        """
        resolved = self._resolve_folder(folder_id)
        return self._http.get(f"/folders/{resolved}/parent", Folder)

    # -------------------------------------------------------------------------
    # Permissions
    # -------------------------------------------------------------------------

    def permissions(self, folder_id: str) -> list[UserGroupAccess]:
        """List folder-level permission overrides (shared groups).

        Args:
            folder_id: Folder UUID or title.
        """
        resolved = self._resolve_folder(folder_id)
        return self._http.get_list(
            f"/folders/{resolved}/permissions", UserGroupAccess
        )

    def effective_permissions(self, folder_id: str) -> EffectivePermissions:
        """Get effective permissions (resolved through the full hierarchy).

        Args:
            folder_id: Folder UUID or title.
        """
        resolved = self._resolve_folder(folder_id)
        return self._http.get(
            f"/folders/{resolved}/effectivepermissions", EffectivePermissions
        )

    def add_permission(self, folder_id: str, group_id: str) -> None:
        """Share a folder with a group (folder-level permission override).

        Adds the group with MEMBER role at the folder level.

        Args:
            folder_id: Folder UUID or title.
            group_id: Group UUID to share with.
        """
        resolved = self._resolve_folder(folder_id)
        validate_input(group_id, "group_id")
        self._http.post_no_content(
            f"/folders/{resolved}/permissions",
            {"groupId": group_id, "role": "MEMBER"},
        )

    def remove_permission(self, folder_id: str, permission_id: str) -> None:
        """Remove a group's folder-level permission override.

        Args:
            folder_id: Folder UUID or title.
            permission_id: Permission UUID to remove (from ``permissions()`` response).
        """
        resolved = self._resolve_folder(folder_id)
        validate_input(permission_id, "permission_id")
        self._http.delete(
            f"/folders/{resolved}/permissions/{permission_id}"
        )

    # -------------------------------------------------------------------------
    # Cross-Collection
    # -------------------------------------------------------------------------

    def move_to_collection(self, folder_id: str, collection_id: str) -> None:
        """Move a folder to a different collection.

        Uses the async bulk operation endpoint. The operation completes
        server-side; this method fires and forgets.

        Args:
            folder_id: Folder UUID or title.
            collection_id: Target collection UUID.
        """
        resolved = self._resolve_folder(folder_id)
        validate_input(collection_id, "collection_id")
        self._http.post_raw(
            "/folders/bulkop",
            {
                "action": {"type": "move-folder", "collectionId": collection_id},
                "items": {"type": "id", "folderIds": [resolved]},
            },
        )

    # -------------------------------------------------------------------------
    # Private — Name Resolution
    # -------------------------------------------------------------------------

    def _resolve_folder(self, folder_id: str) -> str:
        """Resolve a folder identifier to a UUID.

        If *folder_id* is already a UUID, return it directly.
        Otherwise, list all folders and match by title (case-insensitive).
        """
        validate_input(folder_id, "folder_id")

        if is_uuid(folder_id):
            return folder_id

        # Name resolution: list folders and match by title
        folders = self._http.get_list("/folders", Folder)
        for folder in folders:
            if (
                folder.title is not None
                and folder.title.lower() == folder_id.lower()
            ):
                if folder.id is None:
                    raise NotFoundError(
                        f"Folder '{folder_id}' found but has no ID."
                    )
                return folder.id

        raise NotFoundError(
            f"No folder found with title '{folder_id}'. "
            "Pass a folder UUID for exact lookup."
        )
