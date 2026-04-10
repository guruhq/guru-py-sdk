"""Group resource — CRUD, member management, collection access.

Groups are the primary organizational unit for users in Guru. They control
collection access and folder permissions. Members are added/removed by email.

API surface mirrors guru-cli's GroupResource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import quote

from guru_sdk._compat import is_uuid, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models import UserGroup, UserGroupMember
from guru_sdk.models._generated import CollectionModel
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — GroupResource
# =============================================================================


class GroupResource(BaseResource):
    """Guru Groups — CRUD, member management, collection access.

    All methods accept either a group UUID or a group name.
    When a name is passed, it resolves to a UUID via name resolution.
    """

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    def get(self, group_id: str) -> UserGroup:
        """Get a single group by ID or name.

        Args:
            group_id: Group UUID or exact name (case-insensitive).
        """
        resolved = self._resolve_group(group_id)
        return self._http.get(f"/groups/{resolved}", UserGroup)

    def list(self) -> list[UserGroup]:
        """List all groups."""
        return self._http.get_list("/groups", UserGroup)

    def create(self, *, name: str) -> UserGroup:
        """Create a new group.

        Args:
            name: Group name.
        """
        validate_input(name, "name")
        return self._http.post("/groups", {"name": name}, UserGroup)

    def update(self, group_id: str, *, name: str) -> UserGroup:
        """Rename a group.

        Args:
            group_id: Group UUID or name.
            name: New group name.
        """
        resolved = self._resolve_group(group_id)
        validate_input(name, "name")
        return self._http.put(f"/groups/{resolved}", {"name": name}, UserGroup)

    def remove(self, group_id: str) -> None:
        """Delete a group permanently.

        Args:
            group_id: Group UUID or name.
        """
        resolved = self._resolve_group(group_id)
        self._http.delete(f"/groups/{resolved}")

    # -------------------------------------------------------------------------
    # Member Management
    # -------------------------------------------------------------------------

    def members(self, group_id: str) -> builtins.list[UserGroupMember]:
        """List members of a group.

        Args:
            group_id: Group UUID or name.
        """
        resolved = self._resolve_group(group_id)
        return self._http.get_paginated(f"/groups/{resolved}/members", UserGroupMember)

    def add_members(self, group_id: str, *, emails: builtins.list[str]) -> None:
        """Add members to a group by email.

        Args:
            group_id: Group UUID or name.
            emails: List of email addresses to add.
        """
        resolved = self._resolve_group(group_id)
        # API expects a list of objects with "id" set to the email
        body = [{"id": email} for email in emails]
        self._http.post_no_content(f"/groups/{resolved}/members", body)

    def remove_member(self, group_id: str, *, email: str) -> None:
        """Remove a member from a group.

        Args:
            group_id: Group UUID or name.
            email: Email address of the member to remove.
        """
        resolved = self._resolve_group(group_id)
        # Percent-encode the email in the URL path (@ → %40)
        encoded_email = quote(email, safe="")
        self._http.delete(f"/groups/{resolved}/members/{encoded_email}")

    # -------------------------------------------------------------------------
    # Collection Access
    # -------------------------------------------------------------------------

    def collections(self, group_id: str) -> builtins.list[CollectionModel]:
        """List collections a group has access to.

        Args:
            group_id: Group UUID or name.
        """
        resolved = self._resolve_group(group_id)
        return self._http.get_list(f"/groups/{resolved}/collections", CollectionModel)

    # -------------------------------------------------------------------------
    # Private — Name Resolution
    # -------------------------------------------------------------------------

    def _resolve_group(self, group_id: str) -> str:
        """Resolve a group identifier to a UUID.

        If *group_id* is already a UUID, return it directly.
        Otherwise, list all groups and match by name (case-insensitive).
        """
        validate_input(group_id, "group_id")

        if is_uuid(group_id):
            return group_id

        # Name resolution: list groups and match by name
        all_groups = self._http.get_list("/groups", UserGroup)
        for group in all_groups:
            if (
                group.name is not None
                and group.name.lower() == group_id.lower()
            ):
                if group.id is None:
                    raise NotFoundError(
                        f"Group '{group_id}' found but has no ID."
                    )
                return group.id

        raise NotFoundError(
            f"No group found with name '{group_id}'. "
            "Pass a group UUID for exact lookup."
        )
