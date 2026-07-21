"""Tag resource — tag CRUD, category management, team ID resolution.

Tags are labels applied to cards for organization and filtering. Tags live
within tag categories. All tag endpoints require the team ID, which is
resolved once via the /whoami endpoint and cached for the resource lifetime.

API surface mirrors guru-cli's TagResource.
"""

from __future__ import annotations

from guru_sdk._compat import is_uuid, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models import Tag, TagCategory
from guru_sdk.models._generated import WhoAmI
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — TagResource
# =============================================================================


class TagResource(BaseResource):
    """Guru Tags — tag CRUD, category management.

    All tag endpoints require a team ID, which is resolved automatically
    via the /whoami endpoint and cached for the lifetime of this resource.
    """

    # Cache the team ID so we only call /whoami once per resource instance
    _team_id: str | None = None

    def __init__(self, http: object) -> None:
        super().__init__(http)  # type: ignore[arg-type]
        # Instance-level cache (not class-level) so each Guru client is independent
        self._team_id = None

    # -------------------------------------------------------------------------
    # Categories
    # -------------------------------------------------------------------------

    def list_categories(self) -> list[TagCategory]:
        """List all tag categories with their tags."""
        team_id = self._get_team_id()
        return self._http.get_list(f"/teams/{team_id}/tagcategories", TagCategory)

    def create_category(self, *, name: str) -> TagCategory:
        """Create a new tag category.

        Args:
            name: Category name.
        """
        validate_input(name, "name")
        team_id = self._get_team_id()
        return self._http.post(
            f"/teams/{team_id}/tagcategories",
            {"name": name},
            TagCategory,
        )

    def update_category(self, category_id: str, *, name: str) -> TagCategory:
        """Update a tag category's name.

        Args:
            category_id: Category UUID.
            name: New category name.
        """
        validate_input(category_id, "category_id")
        validate_input(name, "name")
        team_id = self._get_team_id()
        return self._http.put(
            f"/teams/{team_id}/tagcategories/{category_id}",
            {"name": name},
            TagCategory,
        )

    def delete_category(self, category_id: str) -> None:
        """Delete a tag category and all its tags.

        Args:
            category_id: Category UUID.
        """
        validate_input(category_id, "category_id")
        team_id = self._get_team_id()
        self._http.delete(f"/teams/{team_id}/tagcategories/{category_id}")

    # -------------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------------

    def get_tag(self, tag_id: str) -> Tag:
        """Get a single tag by ID or name.

        When a non-UUID is passed, searches all categories for a matching
        tag name (case-insensitive).

        Args:
            tag_id: Tag UUID or tag value/name (case-insensitive).
        """
        resolved = self._resolve_tag(tag_id)
        team_id = self._get_team_id()
        return self._http.get(f"/teams/{team_id}/tagcategories/tags/{resolved}", Tag)

    def create_tag(self, *, category_id: str, value: str) -> Tag:
        """Create a new tag in a category.

        Args:
            category_id: Category UUID to create the tag in.
            value: Tag display value.
        """
        validate_input(category_id, "category_id")
        validate_input(value, "value")
        team_id = self._get_team_id()
        return self._http.post(
            f"/teams/{team_id}/tagcategories/tags",
            {"categoryId": category_id, "value": value},
            Tag,
        )

    def update_tag(self, tag_id: str, *, value: str) -> Tag:
        """Update a tag's display value.

        Args:
            tag_id: Tag UUID.
            value: New display value.
        """
        validate_input(tag_id, "tag_id")
        validate_input(value, "value")
        team_id = self._get_team_id()
        return self._http.put(
            f"/teams/{team_id}/tagcategories/tags/{tag_id}",
            {"value": value},
            Tag,
        )

    # -------------------------------------------------------------------------
    # Private — Team ID Resolution
    # -------------------------------------------------------------------------

    def _get_team_id(self) -> str:
        """Resolve the team ID via /whoami, caching the result.

        The team ID is needed for all tag endpoints. We call /whoami once
        and cache the result for the lifetime of this resource instance.
        """
        if self._team_id is not None:
            return self._team_id

        # /whoami returns a WhoAmI object with a required team field
        whoami = self._http.get("/whoami", WhoAmI)
        if whoami.team.id is None:
            raise NotFoundError("Could not resolve team ID from /whoami.")
        self._team_id = whoami.team.id
        return self._team_id

    # -------------------------------------------------------------------------
    # Private — Tag Name Resolution
    # -------------------------------------------------------------------------

    def _resolve_tag(self, tag_id: str) -> str:
        """Resolve a tag identifier to a UUID.

        If *tag_id* is already a UUID, return it directly.
        Otherwise, list all categories and search for a matching tag name
        (case-insensitive).
        """
        validate_input(tag_id, "tag_id")

        if is_uuid(tag_id):
            return tag_id

        # Name resolution: list all categories and search nested tags
        categories = self.list_categories()
        for category in categories:
            if category.tags is None:
                continue
            for tag in category.tags:
                if tag.value is not None and tag.value.lower() == tag_id.lower():
                    if tag.id is None:
                        raise NotFoundError(f"Tag '{tag_id}' found but has no ID.")
                    return tag.id

        raise NotFoundError(f"No tag found with name '{tag_id}'. Pass a tag UUID for exact lookup.")
