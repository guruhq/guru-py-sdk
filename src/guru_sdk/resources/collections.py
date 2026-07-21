"""Collection resource — CRUD, group access management, home folder navigation.

Collections are the top-level organizational unit in Guru. Each collection
contains folders and cards. Group access controls who can read, author, or
administer the collection's content.

API surface mirrors guru-cli's CollectionResource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import builtins

from guru_sdk._compat import is_uuid, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models import CollectionModel, Folder
from guru_sdk.models._generated import UserGroupAccess
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — CollectionResource
# =============================================================================


class CollectionResource(BaseResource):
    """Guru Collections — CRUD, group access, home folder.

    All methods accept either a collection UUID or a collection name.
    When a name is passed, it resolves to a UUID via name resolution.
    """

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    def get(self, collection_id: str) -> CollectionModel:
        """Get a single collection by ID or name.

        Args:
            collection_id: Collection UUID or exact name (case-insensitive).
        """
        resolved = self._resolve_collection(collection_id)
        return self._http.get(f"/collections/{resolved}", CollectionModel)

    def list(self) -> list[CollectionModel]:
        """List all accessible collections."""
        return self._http.get_list("/collections", CollectionModel)

    def create(
        self,
        *,
        name: str,
        description: str | None = None,
        color: str | None = None,
    ) -> CollectionModel:
        """Create a new collection.

        Args:
            name: Collection name.
            description: Optional description.
            color: Optional hex color (e.g., "#4A90D9").
        """
        validate_input(name, "name")

        body: dict[str, Any] = {"name": name}
        if description is not None:
            body["description"] = description
        if color is not None:
            body["color"] = color

        return self._http.post("/collections", body, CollectionModel)

    def update(
        self,
        collection_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        color: str | None = None,
    ) -> CollectionModel:
        """Update an existing collection.

        Only the provided fields are sent — omitted fields are left unchanged.

        Args:
            collection_id: Collection UUID or name.
            name: New name (optional).
            description: New description (optional).
            color: New hex color (optional).
        """
        resolved = self._resolve_collection(collection_id)

        body: dict[str, Any] = {}
        if name is not None:
            validate_input(name, "name")
            body["name"] = name
        if description is not None:
            body["description"] = description
        if color is not None:
            body["color"] = color

        return self._http.put(f"/collections/{resolved}", body, CollectionModel)

    def remove(self, collection_id: str) -> None:
        """Delete a collection permanently.

        Args:
            collection_id: Collection UUID or name.
        """
        resolved = self._resolve_collection(collection_id)
        self._http.delete(f"/collections/{resolved}")

    # -------------------------------------------------------------------------
    # Group Access
    # -------------------------------------------------------------------------

    def groups(self, collection_id: str) -> builtins.list[UserGroupAccess]:
        """List groups with access to a collection.

        Args:
            collection_id: Collection UUID or name.
        """
        resolved = self._resolve_collection(collection_id)
        return self._http.get_list(f"/collections/{resolved}/groups", UserGroupAccess)

    def add_group(self, collection_id: str, group_id: str, *, role: str) -> UserGroupAccess:
        """Add a group to a collection with a specific role.

        Args:
            collection_id: Collection UUID or name.
            group_id: Group UUID.
            role: Access role — "AUTHOR", "MEMBER", or "COLL_ADMIN".
        """
        resolved = self._resolve_collection(collection_id)
        validate_input(group_id, "group_id")
        validate_input(role, "role")
        return self._http.post(
            f"/collections/{resolved}/groups",
            {"groupId": group_id, "role": role},
            UserGroupAccess,
        )

    def update_group(self, collection_id: str, group_id: str, *, role: str) -> UserGroupAccess:
        """Update a group's role on a collection.

        Args:
            collection_id: Collection UUID or name.
            group_id: Group UUID.
            role: New role — "AUTHOR", "MEMBER", or "COLL_ADMIN".
        """
        resolved = self._resolve_collection(collection_id)
        validate_input(group_id, "group_id")
        validate_input(role, "role")
        return self._http.put(
            f"/collections/{resolved}/groups/{group_id}",
            {"groupId": group_id, "role": role},
            UserGroupAccess,
        )

    def remove_group(self, collection_id: str, group_id: str) -> None:
        """Remove a group's access from a collection.

        Args:
            collection_id: Collection UUID or name.
            group_id: Group UUID to remove.
        """
        resolved = self._resolve_collection(collection_id)
        validate_input(group_id, "group_id")
        self._http.delete(f"/collections/{resolved}/groups/{group_id}")

    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    def home_folder(self, collection_id: str) -> Folder:
        """Get a collection's home folder (the root of its folder tree).

        The home folder is identified by ``home=True`` in the folder listing
        filtered by collection.

        Args:
            collection_id: Collection UUID or name.

        Raises:
            NotFoundError: If no home folder exists for the collection.
        """
        resolved = self._resolve_collection(collection_id)
        folders = self._http.get_list("/folders", Folder, collection=resolved)
        for folder in folders:
            if folder.home is True:
                return folder

        raise NotFoundError(f"No home folder found for collection '{collection_id}'.")

    # -------------------------------------------------------------------------
    # Private — Name Resolution
    # -------------------------------------------------------------------------

    def _resolve_collection(self, collection_id: str) -> str:
        """Resolve a collection identifier to a UUID.

        If *collection_id* is already a UUID, return it directly.
        Otherwise, list all collections and match by name (case-insensitive).
        """
        validate_input(collection_id, "collection_id")

        if is_uuid(collection_id):
            return collection_id

        # Name resolution: list collections and match by name
        collections = self._http.get_list("/collections", CollectionModel)
        for coll in collections:
            if coll.name is not None and coll.name.lower() == collection_id.lower():
                if coll.id is None:
                    raise NotFoundError(f"Collection '{collection_id}' found but has no ID.")
                return coll.id

        raise NotFoundError(
            f"No collection found with name '{collection_id}'. "
            "Pass a collection UUID for exact lookup."
        )
