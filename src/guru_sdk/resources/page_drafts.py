"""Page draft resource — CRD + collaborators for Guru Page Drafts.

Page drafts are unpublished page edits. They can be standalone (new page
drafts) or linked to an existing page (edit drafts). This resource provides
create, read, delete operations and collaborator management.

**Update is intentionally omitted.** When a page draft is opened in the web
app, it enters collaborative editing mode (MPS/YJS). Updates from outside that
experience must "politely fail" if the draft is actively being edited. The
update operation will be added in iteration 010a once the architecture supports
detecting and handling the collaborative editing state. This mirrors the same
decision made for card drafts (see DraftResource).

All page draft endpoints are **internal API** — not in the public Swagger spec
but used by guru-cli (see ADR-014).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.errors import ValidationError
from guru_sdk.models._manual import PageDraft, PageDraftCollaborator
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — PageDraftResource
# =============================================================================


class PageDraftResource(BaseResource):
    """Guru Page Drafts — create, read, delete + collaborator management.

    Methods:
        list()                  — list page drafts (GET /pagedrafts)
        get()                   — get by ID (GET /pagedrafts/{id})
        create()                — create (POST /pagedrafts)
        delete()                — delete (DELETE /pagedrafts/{id})
        list_collaborators()    — list collaborators (GET /pagedrafts/{id}/collaborators)
        add_collaborators()     — add collaborators (POST /pagedrafts/{id}/collaborators)
        update_collaborators()  — update collaborators (PUT /pagedrafts/{id}/collaborators)
        remove_collaborator()   — remove collaborator (DELETE /pagedrafts/{id}/collaborators/{cId})

    Update is deferred — see module docstring for rationale.
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self, *, page_id: str | None = None) -> builtins.list[PageDraft]:
        """List page drafts, optionally filtered by page ID.

        Args:
            page_id: If provided, only return drafts for this page.
        """
        if page_id is not None:
            validate_input(page_id, "page_id")
            return self._http.get_list("/pagedrafts", PageDraft, pageId=page_id)
        return self._http.get_list("/pagedrafts", PageDraft)

    def get(self, page_draft_id: str) -> PageDraft:
        """Get a page draft by ID.

        Args:
            page_draft_id: Page draft UUID.
        """
        validate_input(page_draft_id, "page_draft_id")
        return self._http.get(f"/pagedrafts/{page_draft_id}", PageDraft)

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def create(
        self,
        *,
        title: str,
        page_id: str | None = None,
        json_content: str | None = None,
        hero_image: str | None = None,
        badge_emoji: str | None = None,
        parent_page_id: str | None = None,
        knowledge_agent_id: str | None = None,
    ) -> PageDraft:
        """Create a new page draft.

        Args:
            title: Draft title (required).
            page_id: Link draft to an existing page (creates an edit draft).
            json_content: Slate JSON content.
            hero_image: URL for the hero image.
            badge_emoji: Emoji badge (e.g. ":star:").
            parent_page_id: ID of the parent page.
            knowledge_agent_id: ID of the default Knowledge Agent.
        """
        validate_free_text(title, "title")
        if not title.strip():
            raise ValidationError("title must not be empty")
        if page_id is not None:
            validate_input(page_id, "page_id")
        if parent_page_id is not None:
            validate_input(parent_page_id, "parent_page_id")
        if knowledge_agent_id is not None:
            validate_input(knowledge_agent_id, "knowledge_agent_id")

        body: dict[str, Any] = {"title": title}
        if page_id is not None:
            body["pageId"] = page_id
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
        return self._http.post("/pagedrafts", body, PageDraft)

    def delete(self, page_draft_id: str) -> None:
        """Delete a page draft.

        Args:
            page_draft_id: Page draft UUID.
        """
        validate_input(page_draft_id, "page_draft_id")
        self._http.delete(f"/pagedrafts/{page_draft_id}")

    # -------------------------------------------------------------------------
    # Collaborators
    # -------------------------------------------------------------------------

    def list_collaborators(self, page_draft_id: str) -> builtins.list[PageDraftCollaborator]:
        """List collaborators on a page draft.

        Args:
            page_draft_id: Page draft UUID.
        """
        validate_input(page_draft_id, "page_draft_id")
        return self._http.get_list(
            f"/pagedrafts/{page_draft_id}/collaborators",
            PageDraftCollaborator,
        )

    def add_collaborators(
        self,
        page_draft_id: str,
        collaborators: builtins.list[dict[str, Any]],
    ) -> builtins.list[PageDraftCollaborator]:
        """Add collaborators to a page draft.

        Args:
            page_draft_id: Page draft UUID.
            collaborators: List of collaborator dicts with 'type' and optional 'objectRole'.
        """
        validate_input(page_draft_id, "page_draft_id")
        return self._http.post_list(
            f"/pagedrafts/{page_draft_id}/collaborators",
            {"collaborators": collaborators},
            PageDraftCollaborator,
        )

    def update_collaborators(
        self,
        page_draft_id: str,
        collaborators: builtins.list[dict[str, Any]],
    ) -> builtins.list[PageDraftCollaborator]:
        """Update collaborator roles on a page draft.

        Args:
            page_draft_id: Page draft UUID.
            collaborators: List of collaborator dicts with updated roles.
        """
        validate_input(page_draft_id, "page_draft_id")
        return self._http.put_list(
            f"/pagedrafts/{page_draft_id}/collaborators",
            PageDraftCollaborator,
            {"collaborators": collaborators},
        )

    def remove_collaborator(self, page_draft_id: str, collaborator_id: str) -> None:
        """Remove a collaborator from a page draft.

        Args:
            page_draft_id: Page draft UUID.
            collaborator_id: Collaborator UUID.
        """
        validate_input(page_draft_id, "page_draft_id")
        validate_input(collaborator_id, "collaborator_id")
        self._http.delete(f"/pagedrafts/{page_draft_id}/collaborators/{collaborator_id}")
