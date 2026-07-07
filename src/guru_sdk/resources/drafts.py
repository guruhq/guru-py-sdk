"""Draft resource — CRD + collaborators for draft cards.

Drafts are unpublished card edits. They can be standalone (new card drafts) or
linked to an existing card (edit drafts). This resource provides create, read,
delete operations and collaborator management.

**Update is intentionally omitted.** When a draft is opened in the web app, it
enters collaborative editing mode (MPS/YJS). Updates from outside that
experience must "politely fail" if the draft is actively being edited. The
update operation will be added in a future iteration once the architecture
supports detecting and handling the collaborative editing state.

API surface mirrors guru-cli's DraftResource (CRD subset + collaborators).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.errors import ValidationError
from guru_sdk.models._generated import DraftCard
from guru_sdk.models._manual import DraftCollaborator
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    import builtins

# =============================================================================
# Public API — DraftResource
# =============================================================================


class DraftResource(BaseResource):
    """Guru Drafts — create, read, and delete draft cards.

    Methods:
        list()                     — list all drafts or filter by card ID (GET /drafts)
        get()                      — get a draft by ID (GET /drafts/{draftId})
        create()                   — create a new draft (POST /drafts)
        delete()                   — delete a draft (DELETE /drafts/{draftId})
        list_collaborators()       — list collaborators (GET /drafts/{id}/collaborators)
        add_collaborators()        — add collaborators (POST /drafts/{id}/collaborators)
        add_group_collaborators()  — add group collaborators (POST /drafts/{id}/collaborators)
        remove_collaborator()      — remove collaborator (DELETE /drafts/{id}/collaborators/{cId})
        remove_group_collaborator() — remove group collaborator (DELETE /drafts/{id}/collaborators/{gId})

    Update is deferred — see module docstring for rationale.
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self, *, card_id: str | None = None) -> list[DraftCard]:
        """List drafts, optionally filtered by card ID.

        Args:
            card_id: If provided, only return drafts for this card.
        """
        if card_id is not None:
            validate_input(card_id, "card_id")
            return self._http.get_list("/drafts", DraftCard, cardId=card_id)
        return self._http.get_list("/drafts", DraftCard)

    def get(self, draft_id: str) -> DraftCard:
        """Get a draft by ID.

        Args:
            draft_id: Draft UUID.
        """
        validate_input(draft_id, "draft_id")
        return self._http.get(f"/drafts/{draft_id}", DraftCard)

    # -------------------------------------------------------------------------
    # Create
    # -------------------------------------------------------------------------

    def create(
        self,
        *,
        title: str,
        content: str | None = None,
        json_content: str | None = None,
        card_id: str | None = None,
    ) -> DraftCard:
        """Create a new draft card.

        Args:
            title: Draft title (required).
            content: HTML content body.
            json_content: Slate JSON content. Pass empty string "" to have
                          the server auto-convert from HTML content.
            card_id: Link draft to an existing card (creates an edit draft).
                     Omit for a standalone new-card draft.
        """
        validate_free_text(title, "title")
        if not title.strip():
            raise ValidationError("title must not be empty")
        body: dict[str, Any] = {"title": title}
        if content is not None:
            body["content"] = content
        if json_content is not None:
            body["jsonContent"] = json_content
        if card_id is not None:
            validate_input(card_id, "card_id")
            body["cardId"] = card_id
        return self._http.post("/drafts", body, DraftCard)

    # -------------------------------------------------------------------------
    # Delete
    # -------------------------------------------------------------------------

    def delete(self, draft_id: str) -> None:
        """Delete a draft.

        Args:
            draft_id: Draft UUID.
        """
        validate_input(draft_id, "draft_id")
        self._http.delete(f"/drafts/{draft_id}")

    # -------------------------------------------------------------------------
    # Collaborators — manage who can see/edit a draft
    # -------------------------------------------------------------------------

    def list_collaborators(self, draft_id: str) -> builtins.list[DraftCollaborator]:
        """List collaborators on a draft.

        Args:
            draft_id: Draft UUID.
        """
        validate_input(draft_id, "draft_id")
        return self._http.get_list(
            f"/drafts/{draft_id}/collaborators",
            DraftCollaborator,
        )

    def add_collaborators(
        self,
        draft_id: str,
        collaborators: builtins.list[dict[str, Any]],
    ) -> builtins.list[DraftCollaborator]:
        """Add collaborators to a draft.

        Args:
            draft_id: Draft UUID.
            collaborators: List of collaborator dicts, each with 'type' (e.g.
                "user") and a nested 'user' (e.g. ``{"email": ...}``) or 'group'.
        """
        validate_input(draft_id, "draft_id")
        return self._http.post_list(
            f"/drafts/{draft_id}/collaborators",
            {"collaborators": collaborators},
            DraftCollaborator,
        )

    def add_group_collaborators(
        self,
        draft_id: str,
        group_ids: builtins.list[str],
    ) -> builtins.list[DraftCollaborator]:
        """Add group collaborators to a draft.

        Args:
            draft_id: Draft UUID.
            group_ids: List of group UUIDs to add as collaborators.
        """
        validate_input(draft_id, "draft_id")
        if not group_ids:
            raise ValidationError("group_ids must not be empty")
        for gid in group_ids:
            validate_input(gid, "group_id")
        collaborators = [{"type": "user-group", "userGroup": {"id": gid}} for gid in group_ids]
        return self._http.post_list(
            f"/drafts/{draft_id}/collaborators",
            {"collaborators": collaborators},
            DraftCollaborator,
        )

    def remove_collaborator(self, draft_id: str, collaborator_id: str) -> None:
        """Remove a collaborator from a draft.

        Args:
            draft_id: Draft UUID.
            collaborator_id: Collaborator ID.
        """
        validate_input(draft_id, "draft_id")
        validate_input(collaborator_id, "collaborator_id")
        self._http.delete(f"/drafts/{draft_id}/collaborators/{collaborator_id}")

    def remove_group_collaborator(self, draft_id: str, group_id: str) -> None:
        """Remove a group collaborator from a draft.

        For group collaborators the collaborator ID is the group UUID.

        Args:
            draft_id: Draft UUID.
            group_id: Group UUID (used as the collaborator ID).
        """
        validate_input(draft_id, "draft_id")
        validate_input(group_id, "group_id")
        self.remove_collaborator(draft_id, group_id)
