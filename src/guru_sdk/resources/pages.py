"""Page resource — CRUD, hierarchy, permissions for Guru Pages.

Pages are the top-level content containers in Guru (replacing the legacy
"board" concept). They form a tree hierarchy with sub-pages, support
permissions at the page level, and can be linked to Knowledge Agents.

All page endpoints are **internal API** — they are not in the public Swagger
spec but are used by guru-cli (see ADR-014). They work in practice with
standard API tokens.

API surface mirrors guru-cli's PageResource.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import Page
from guru_sdk.models._manual import PagePermission
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — PageResource
# =============================================================================


class PageResource(BaseResource):
    """Guru Pages — CRUD, hierarchy traversal, permissions.

    Methods:
        list()              — list all pages (GET /pages)
        get()               — get a page by ID (GET /pages/{pageId})
        list_nested()       — get nested tree (GET /pages/nested)
        create()            — create a page (POST /pages)
        update()            — update a page (PUT /pages/{pageId})
        delete()            — delete a page (DELETE /pages/{pageId})
        move()              — reposition a page (PUT /pages/{pageId}/position)
        list_permissions()  — list permissions (GET /pages/{pageId}/permissions)
        add_permissions()   — add permissions (POST /pages/{pageId}/permissions)
        update_permission() — update permission (PUT /pages/{pageId}/permissions/{id})
        remove_permission() — remove permission (DELETE /pages/{pageId}/permissions/{id})
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self) -> builtins.list[Page]:
        """List all pages for the team."""
        return self._http.get_list("/pages", Page)

    def get(self, page_id: str) -> Page:
        """Get a page by ID.

        Args:
            page_id: Page UUID.
        """
        validate_input(page_id, "page_id")
        return self._http.get(f"/pages/{page_id}", Page)

    def list_nested(self, *, view_only: bool = False) -> Page:
        """Get pages in a nested tree structure.

        Returns a root Page with sub_pages populated recursively.

        Args:
            view_only: If True, only return pages visible to the current user.
        """
        path = "/pages/nested?viewOnly=true" if view_only else "/pages/nested"
        return self._http.get(path, Page)

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def create(
        self,
        *,
        title: str,
        json_content: str | None = None,
        hero_image: str | None = None,
        badge_emoji: str | None = None,
        parent_page_id: str | None = None,
        knowledge_agent_id: str | None = None,
        draft_id: str | None = None,
        only_navigable: bool | None = None,
    ) -> Page:
        """Create a new page.

        Args:
            title: Page title (required).
            json_content: Slate JSON content.
            hero_image: URL for the hero image.
            badge_emoji: Emoji badge (e.g. ":star:").
            parent_page_id: ID of the parent page.
            knowledge_agent_id: ID of the default Knowledge Agent.
            draft_id: ID of a draft to publish as this page.
            only_navigable: If True, page is navigation-only (no content).
        """
        validate_free_text(title, "title")
        if not title.strip():
            raise ValidationError("title must not be empty")
        if parent_page_id is not None:
            validate_input(parent_page_id, "parent_page_id")
        if knowledge_agent_id is not None:
            validate_input(knowledge_agent_id, "knowledge_agent_id")
        if draft_id is not None:
            validate_input(draft_id, "draft_id")

        body: dict[str, Any] = {"title": title}
        if json_content is not None:
            body["jsonContent"] = json_content
        if hero_image is not None:
            body["heroImage"] = hero_image
        if badge_emoji is not None:
            body["badgeEmoji"] = badge_emoji
        if parent_page_id is not None:
            body["parentPageId"] = parent_page_id
        if knowledge_agent_id is not None:
            body["knowledgeAgentId"] = knowledge_agent_id
        if draft_id is not None:
            body["draftId"] = draft_id
        if only_navigable is not None:
            body["onlyNavigable"] = only_navigable
        return self._http.post("/pages", body, Page)

    def update(
        self,
        page_id: str,
        *,
        title: str | None = None,
        json_content: str | None = None,
        hero_image: str | None = None,
        badge_emoji: str | None = None,
        parent_page_id: str | None = None,
        knowledge_agent_id: str | None = None,
        only_navigable: bool | None = None,
    ) -> Page:
        """Update an existing page.

        Args:
            page_id: Page UUID.
            title: New title.
            json_content: New Slate JSON content.
            hero_image: New hero image URL.
            badge_emoji: New emoji badge.
            parent_page_id: New parent page ID.
            knowledge_agent_id: New Knowledge Agent ID.
            only_navigable: Navigation-only flag.
        """
        validate_input(page_id, "page_id")
        if title is not None:
            validate_free_text(title, "title")
        if parent_page_id is not None:
            validate_input(parent_page_id, "parent_page_id")
        if knowledge_agent_id is not None:
            validate_input(knowledge_agent_id, "knowledge_agent_id")

        body: dict[str, Any] = {}
        if title is not None:
            body["title"] = title
        if json_content is not None:
            body["jsonContent"] = json_content
        if hero_image is not None:
            body["heroImage"] = hero_image
        if badge_emoji is not None:
            body["badgeEmoji"] = badge_emoji
        if parent_page_id is not None:
            body["parentPageId"] = parent_page_id
        if knowledge_agent_id is not None:
            body["knowledgeAgentId"] = knowledge_agent_id
        if only_navigable is not None:
            body["onlyNavigable"] = only_navigable
        return self._http.put(f"/pages/{page_id}", body, Page)

    def delete(self, page_id: str) -> None:
        """Delete a page.

        Args:
            page_id: Page UUID.
        """
        validate_input(page_id, "page_id")
        self._http.delete(f"/pages/{page_id}")

    def move(
        self,
        page_id: str,
        *,
        parent_page_id: str | None = None,
        prev_sibling_page_id: str | None = None,
    ) -> Page:
        """Move a page to a new position in the hierarchy.

        Args:
            page_id: Page UUID to move.
            parent_page_id: New parent page ID.
            prev_sibling_page_id: Page ID of the previous sibling, or "first"/"last"
                                  for position anchors.
        """
        validate_input(page_id, "page_id")
        if parent_page_id is not None:
            validate_input(parent_page_id, "parent_page_id")
        # prev_sibling_page_id can be "first" or "last" — only validate if it
        # looks like a real ID (not a position anchor keyword)
        if (
            prev_sibling_page_id is not None
            and prev_sibling_page_id not in ("first", "last")
        ):
            validate_input(prev_sibling_page_id, "prev_sibling_page_id")

        body: dict[str, Any] = {}
        if parent_page_id is not None:
            body["parentPageId"] = parent_page_id
        if prev_sibling_page_id is not None:
            body["prevSiblingPageId"] = prev_sibling_page_id
        return self._http.put(f"/pages/{page_id}/position", body, Page)

    # -------------------------------------------------------------------------
    # Permissions
    # -------------------------------------------------------------------------

    def list_permissions(self, page_id: str) -> builtins.list[PagePermission]:
        """List permissions on a page.

        Args:
            page_id: Page UUID.
        """
        validate_input(page_id, "page_id")
        return self._http.get_list(f"/pages/{page_id}/permissions", PagePermission)

    def add_permissions(
        self,
        page_id: str,
        permissions: builtins.list[dict[str, Any]],
    ) -> builtins.list[PagePermission]:
        """Add permissions to a page.

        Args:
            page_id: Page UUID.
            permissions: List of permission dicts with 'type' and 'permissionType'.
        """
        validate_input(page_id, "page_id")
        return self._http.post_list(
            f"/pages/{page_id}/permissions",
            {"permissions": permissions},
            PagePermission,
        )

    def update_permission(
        self,
        page_id: str,
        permission_id: str,
        permission: dict[str, Any],
    ) -> None:
        """Update a single permission on a page.

        Args:
            page_id: Page UUID.
            permission_id: Permission UUID.
            permission: Updated permission dict.
        """
        validate_input(page_id, "page_id")
        validate_input(permission_id, "permission_id")
        self._http.put_no_content(
            f"/pages/{page_id}/permissions/{permission_id}",
            permission,
        )

    def remove_permission(self, page_id: str, permission_id: str) -> None:
        """Remove a permission from a page.

        Args:
            page_id: Page UUID.
            permission_id: Permission UUID.
        """
        validate_input(page_id, "page_id")
        validate_input(permission_id, "permission_id")
        self._http.delete(f"/pages/{page_id}/permissions/{permission_id}")
