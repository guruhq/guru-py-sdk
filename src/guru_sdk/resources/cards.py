"""Card resource — full CRUD, verification, tags, comments, folders, collaborators.

The most complex resource module. Proves the end-to-end pattern that all
subsequent resources will follow: model + resource + tests + wired into Guru
facade.

API surface mirrors guru-cli's CardResource exactly — same method names, same
endpoint paths, same vocabulary. Knowledge transfers between the two codebases.
"""

from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import quote

from guru_sdk._compat import is_uuid, validate_free_text, validate_input
from guru_sdk.errors import NotFoundError
from guru_sdk.models import (
    Card,
    CardCollaborator,
    CardComment,
    CardCommentReply,
    CardCommentResult,
    CardVerifier,
    Folder,
    Tag,
)
from guru_sdk.resources._base import BaseResource

if TYPE_CHECKING:
    from guru_sdk.http import PaginatedList

# =============================================================================
# Public API — CardResource
# =============================================================================


class CardResource(BaseResource):
    """Guru Cards — CRUD, verification, tags, comments, folders, collaborators.

    All methods accept either a card UUID or a card title. When a title is
    passed, it resolves to a UUID via name resolution (list + case-insensitive
    match).
    """

    # -------------------------------------------------------------------------
    # CRUD
    # -------------------------------------------------------------------------

    def get(self, card_id: str) -> Card:
        """Get a single card by ID or title.

        Args:
            card_id: Card UUID or exact title (case-insensitive).

        Returns:
            The resolved Card.

        Raises:
            NotFoundError: If the card doesn't exist or title doesn't match.
            ValidationError: If the input contains invalid characters.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get(f"/cards/{resolved}", Card)

    def create(
        self,
        *,
        title: str,
        content: str,
        collection_id: str,
        share_status: str = "TEAM",
    ) -> Card:
        """Create a new card.

        Args:
            title: The card's preferred phrase (display name).
            content: HTML content of the card body.
            collection_id: UUID of the collection to create the card in.
            share_status: Sharing level — "TEAM", "PRIVATE", etc. Defaults to "TEAM".

        Returns:
            The newly created Card.
        """
        validate_input(title, "title")
        validate_input(collection_id, "collection_id")
        # Content is HTML authored by users — use lenient free-text validation
        validate_free_text(content, "content")

        body: dict[str, Any] = {
            "preferredPhrase": title,
            "content": content,
            "collection": {"id": collection_id},
            "shareStatus": share_status,
        }
        return self._http.post("/cards/extended", body, Card)

    def update(
        self,
        card_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
    ) -> Card:
        """Update an existing card.

        Only the provided fields are sent — omitted fields are left unchanged.

        Args:
            card_id: Card UUID or title.
            title: New preferred phrase (optional).
            content: New HTML content (optional).

        Returns:
            The updated Card.
        """
        resolved = self._resolve_card(card_id)

        body: dict[str, Any] = {}
        if title is not None:
            validate_input(title, "title")
            body["preferredPhrase"] = title
        if content is not None:
            validate_free_text(content, "content")
            body["content"] = content

        return self._http.put(f"/cards/{resolved}/extended", body, Card)

    def patch(
        self,
        card_id: str,
        *,
        title: str | None = None,
        content: str | None = None,
        keep_verification: bool = True,
    ) -> Card:
        """Patch card content/title with optional verification preservation.

        Unlike ``update()``, which uses PUT and always triggers re-verification,
        ``patch()`` uses PATCH with ``keepVerificationState=True`` by default.
        This lets collection owners edit card content without unverifying it.

        Args:
            card_id: Card UUID or title.
            title: New preferred phrase (optional).
            content: New HTML content (optional).
            keep_verification: If True (default), the card's verification state
                is preserved. Set to False to trigger re-verification.

        Returns:
            The patched Card.
        """
        resolved = self._resolve_card(card_id)

        body: dict[str, Any] = {}
        if title is not None:
            validate_input(title, "title")
            body["preferredPhrase"] = title
        if content is not None:
            validate_free_text(content, "content")
            body["content"] = content

        keep = "true" if keep_verification else "false"
        return self._http.patch(
            f"/cards/{resolved}",
            body,
            Card,
            keepVerificationState=keep,
        )

    def remove(self, card_id: str) -> None:
        """Delete a card permanently.

        For soft-delete (archival), use ``archive()`` instead — same API
        endpoint, but ``archive`` makes the intent clearer and pairs with
        ``restore()``.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        self._http.delete(f"/cards/{resolved}")

    def archive(self, card_id: str) -> None:
        """Archive a card (soft delete — can be restored).

        This uses the same DELETE endpoint as ``remove()``, but the name
        reflects the py-sdk convention: Guru's DELETE is a soft delete.
        Use ``restore()`` to bring it back.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        self._http.delete(f"/cards/{resolved}")

    def restore(self, card_id: str) -> None:
        """Restore an archived card.

        Args:
            card_id: Card UUID to restore. Must be a UUID (not a title,
                since archived cards can't be listed by name).
        """
        validate_input(card_id, "card_id")
        self._http.post_raw(
            "/cards/bulkop",
            {
                "action": {"type": "restore-archived-card"},
                "items": {"type": "id", "cardIds": [card_id]},
            },
        )

    def get_version(self, card_id: str, version: int) -> Card:
        """Retrieve a historical version of a card.

        Args:
            card_id: Card UUID or title.
            version: Version number to retrieve.

        Returns:
            The Card at the specified version.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get(f"/cards/{resolved}/versions/{version}", Card)

    def get_bulk(self, card_ids: list[str]) -> list[Card]:
        """Retrieve multiple cards in a single request.

        Args:
            card_ids: List of card UUIDs to fetch.

        Returns:
            List of Card objects.
        """
        for cid in card_ids:
            validate_input(cid, "card_id")
        return self._http.post_list("/cards/bulk", card_ids, Card)

    def move_to_collection(self, card_id: str, collection_id: str) -> None:
        """Move a card to a different collection.

        Uses the async bulk operation endpoint. The operation completes
        server-side; this method fires and forgets.

        Args:
            card_id: Card UUID or title.
            collection_id: Target collection UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(collection_id, "collection_id")
        self._http.post_raw(
            "/cards/bulkop",
            {
                "action": {"type": "move-card", "collectionId": collection_id},
                "items": {"type": "id", "cardIds": [resolved]},
            },
        )

    def download_pdf(self, card_id: str) -> bytes:
        """Download a card as a PDF.

        Args:
            card_id: Card UUID or title.

        Returns:
            Raw PDF bytes. Write to a file with ``open(path, "wb").write(result)``.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get_bytes(f"/cards/{resolved}/pdf")

    def favorite(self, card_id: str) -> None:
        """Add a card to the user's favorites.

        Note: The Guru favorites API is complex (uses favorite lists).
        This method uses the simpler card-level approach. For the full
        favorite list management, use the favorites resource (Phase 3).

        Args:
            card_id: Card UUID or title.
        """
        # TODO: Implement full favorites support via favorite lists endpoint
        # For now, this is a placeholder — the full implementation needs
        # the favorite list ID, which requires a separate API call.
        # The unfavorite endpoint is straightforward (DELETE /cards/{id}/favorite).
        _ = self._resolve_card(card_id)  # validate input even though we can't proceed
        msg = (
            "favorite() is not yet fully implemented. "
            "The Guru favorites API requires fetching favorite lists first. "
            "Use the Guru web UI for now, or call unfavorite() to remove."
        )
        raise NotImplementedError(msg)

    def unfavorite(self, card_id: str) -> None:
        """Remove a card from the user's favorites.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        self._http.delete(f"/cards/{resolved}/favorite")

    # -------------------------------------------------------------------------
    # Verification
    # -------------------------------------------------------------------------

    def verify(self, card_id: str) -> Card:
        """Mark a card as verified (trusted).

        Args:
            card_id: Card UUID or title.

        Returns:
            The verified Card with updated verification state.
        """
        resolved = self._resolve_card(card_id)
        return self._http.put_empty(f"/cards/{resolved}/verify", Card)

    def unverify(self, card_id: str) -> None:
        """Mark a card as unverified.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        self._http.post_no_content(f"/cards/{resolved}/unverify")

    def list_unverified(self) -> list[Card]:
        """List all cards needing verification.

        Returns:
            List of cards in the verification queue.
        """
        return self._http.get_list("/cards/verificationmgr", Card)

    # -------------------------------------------------------------------------
    # Tags
    # -------------------------------------------------------------------------

    def list_tags(self, card_id: str) -> list[Tag]:
        """List tags on a card.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get_list(f"/cards/{resolved}/tags", Tag)

    def add_tag(self, card_id: str, tag_id: str) -> list[Tag]:
        """Add a tag to a card.

        Args:
            card_id: Card UUID or title.
            tag_id: Tag UUID to add.

        Returns:
            The updated list of tags on the card.
        """
        resolved = self._resolve_card(card_id)
        validate_input(tag_id, "tag_id")
        return self._http.put_list(f"/cards/{resolved}/tags/{tag_id}", Tag)

    def remove_tag(self, card_id: str, tag_id: str) -> None:
        """Remove a tag from a card.

        Args:
            card_id: Card UUID or title.
            tag_id: Tag UUID to remove.
        """
        resolved = self._resolve_card(card_id)
        validate_input(tag_id, "tag_id")
        self._http.delete(f"/cards/{resolved}/tags/{tag_id}")

    # -------------------------------------------------------------------------
    # Comments
    # -------------------------------------------------------------------------

    def list_comments(self, card_id: str, *, status: str | None = None) -> list[CardComment]:
        """List comments on a card.

        Args:
            card_id: Card UUID or title.
            status: Filter by comment status — "OPEN" or "RESOLVED".
                If None, returns all comments.
        """
        resolved = self._resolve_card(card_id)
        if status is not None:
            return self._http.get_list(f"/cards/{resolved}/comments", CardComment, status=status)
        return self._http.get_list(f"/cards/{resolved}/comments", CardComment)

    def bulk_get_comments(
        self,
        *,
        status: str | None = None,
        created_after: str | None = None,
        created_before: str | None = None,
        max_pages: int = 10,
    ) -> PaginatedList[CardCommentResult]:
        """Bulk-retrieve card comment threads across all accessible cards.

        Consumes the team-wide GET /api/v1/comments endpoint. Results are
        access-scoped to the caller, newest-activity first, and paginated via
        Link headers.

        Args:
            status: Filter top-level comments by status — "OPEN" or "RESOLVED".
            created_after / created_before: ISO-8601 bounds on the thread's
                most-recent activity (inclusive).
            max_pages: Safety cap on pages walked (default 10).

        Returns a :class:`PaginatedList`; check its ``complete`` attribute to
        detect when ``max_pages`` truncated the result before all matching
        comments were retrieved.
        """
        params: dict[str, Any] = {}
        if status is not None:
            validate_input(status, "status")
            params["status"] = status
        if created_after is not None:
            validate_input(created_after, "created_after")
            params["createdAfter"] = created_after
        if created_before is not None:
            validate_input(created_before, "created_before")
            params["createdBefore"] = created_before
        return self._http.get_paginated(
            "/comments", CardCommentResult, max_pages=max_pages, **params
        )

    def add_comment(self, card_id: str, content: str) -> CardComment:
        """Add a comment to a card.

        Args:
            card_id: Card UUID or title.
            content: Comment text. Uses free-text validation (question marks allowed).
        """
        resolved = self._resolve_card(card_id)
        # Comments are natural language — use lenient validation
        validate_free_text(content, "comment content")
        return self._http.post(f"/cards/{resolved}/comments", {"content": content}, CardComment)

    def delete_comment(self, card_id: str, comment_id: str) -> None:
        """Delete a comment from a card.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        self._http.delete(f"/cards/{resolved}/comments/{comment_id}")

    def update_comment(self, card_id: str, comment_id: str, content: str) -> CardComment:
        """Update an existing comment's content.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
            content: New comment text.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        validate_free_text(content, "comment content")
        return self._http.put(
            f"/cards/{resolved}/comments/{comment_id}",
            {"content": content},
            CardComment,
        )

    def reply_comment(self, card_id: str, comment_id: str, content: str) -> CardCommentReply:
        """Reply to a comment on a card.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
            content: Reply text.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        validate_free_text(content, "reply content")
        return self._http.post(
            f"/cards/{resolved}/comments/{comment_id}/replies",
            {"content": content},
            CardCommentReply,
        )

    def delete_reply(self, card_id: str, comment_id: str, reply_id: str) -> None:
        """Delete a reply from a comment.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
            reply_id: Reply UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        validate_input(reply_id, "reply_id")
        self._http.delete(f"/cards/{resolved}/comments/{comment_id}/replies/{reply_id}")

    def resolve_comment(self, card_id: str, comment_id: str) -> None:
        """Resolve a comment on a card.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        self._http.put_no_content(f"/cards/{resolved}/comments/{comment_id}/resolve")

    def unresolve_comment(self, card_id: str, comment_id: str) -> None:
        """Unresolve a comment on a card.

        Args:
            card_id: Card UUID or title.
            comment_id: Comment UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(comment_id, "comment_id")
        self._http.put_no_content(f"/cards/{resolved}/comments/{comment_id}/unresolve")

    # -------------------------------------------------------------------------
    # Folders
    # -------------------------------------------------------------------------

    def list_folders(self, card_id: str) -> list[Folder]:
        """List folders a card belongs to.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get_list(f"/cards/{resolved}/folders", Folder)

    def add_to_folder(self, card_id: str, folder_id: str) -> Folder:
        """Add a card to a folder.

        Args:
            card_id: Card UUID or title.
            folder_id: Folder UUID.

        Returns:
            The Folder the card was added to.
        """
        resolved = self._resolve_card(card_id)
        validate_input(folder_id, "folder_id")
        return self._http.post(f"/cards/{resolved}/folders", {"id": folder_id}, Folder)

    def remove_from_folder(self, card_id: str, folder_id: str) -> None:
        """Remove a card from a folder.

        Args:
            card_id: Card UUID or title.
            folder_id: Folder UUID.
        """
        resolved = self._resolve_card(card_id)
        validate_input(folder_id, "folder_id")
        self._http.delete(f"/cards/{resolved}/folders/{folder_id}")

    # -------------------------------------------------------------------------
    # Collaborators
    # -------------------------------------------------------------------------

    def list_collaborators(self, card_id: str) -> list[CardCollaborator]:
        """List collaborators on a card.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get_list(f"/cards/{resolved}/collaborators", CardCollaborator)

    def add_collaborator(self, card_id: str, email: str) -> list[CardCollaborator]:
        """Add a collaborator to a card.

        Args:
            card_id: Card UUID or title.
            email: Email address of the user to add.

        Returns:
            The updated list of collaborators.
        """
        resolved = self._resolve_card(card_id)
        # Email contains @ which is valid — but validate for control chars
        validate_free_text(email, "collaborator email")
        # API expects an array of collaborator objects
        body = [{"type": "user", "user": {"email": email}}]
        return self._http.post_list(f"/cards/{resolved}/collaborators", body, CardCollaborator)

    def remove_collaborator(self, card_id: str, email: str) -> None:
        """Remove a collaborator from a card.

        Args:
            card_id: Card UUID or title.
            email: Email address of the user to remove.
        """
        resolved = self._resolve_card(card_id)
        validate_free_text(email, "collaborator email")
        # URL-encode email because @ needs percent-encoding in URL paths
        encoded_email = quote(email, safe="")
        self._http.delete(f"/cards/{resolved}/collaborators/{encoded_email}")

    # -------------------------------------------------------------------------
    # Verifiers
    # -------------------------------------------------------------------------

    def list_verifiers(self, card_id: str) -> list[CardVerifier]:
        """List verifiers assigned to a card.

        Args:
            card_id: Card UUID or title.
        """
        resolved = self._resolve_card(card_id)
        return self._http.get_list(f"/cards/{resolved}/verifiers", CardVerifier)

    # -------------------------------------------------------------------------
    # Attachments
    # -------------------------------------------------------------------------

    def upload_file(self, file_path: str | Path) -> str:
        """Upload a file to Guru and return a URL for embedding in card content.

        The returned URL can be used in card HTML, e.g.::

            url = g.cards.upload_file("diagram.png")
            g.cards.update(card_id, content=f'<img src="{url}">')

        Supports images, PDFs, and other file types. Uses the
        ``POST /attachments/upload`` endpoint (not in public Swagger spec —
        see ADR-006).

        Args:
            file_path: Path to the local file (str or pathlib.Path).

        Returns:
            The attachment URL (e.g., ``https://content.api.getguru.com/files/view/...``).

        Raises:
            FileNotFoundError: If the file doesn't exist.
        """
        path = Path(file_path)
        if not path.exists():
            msg = f"File not found: {path}"
            raise FileNotFoundError(msg)

        # Guess MIME type from extension, fall back to binary stream
        mimetype = _guess_mimetype(path.name)
        file_bytes = path.read_bytes()

        result = self._http.post_file(
            "/attachments/upload",
            field_name="file",
            filename=path.name,
            file_bytes=file_bytes,
            mimetype=mimetype,
        )
        # Response shape: {"attachmentId": "...", "link": "...", ...}
        link: str = result.get("link", "")
        return link

    # -------------------------------------------------------------------------
    # Private — Name Resolution
    # -------------------------------------------------------------------------

    def _resolve_card(self, card_id: str) -> str:
        """Resolve a card identifier to a UUID.

        If *card_id* is already a UUID, return it directly after validation.
        Otherwise, list cards from the verification queue and match by
        preferred_phrase (case-insensitive).

        Returns:
            The card UUID.

        Raises:
            NotFoundError: If no card matches the given title.
            ValidationError: If the input contains invalid characters.
        """
        validate_input(card_id, "card_id")

        if is_uuid(card_id):
            return card_id

        # Name resolution: list cards and match by title (case-insensitive).
        # Uses the verification manager endpoint as a broad card listing source.
        cards = self._http.get_list("/cards/verificationmgr", Card)
        for card in cards:
            if (
                card.preferred_phrase is not None
                and card.preferred_phrase.lower() == card_id.lower()
            ):
                if card.id is None:
                    raise NotFoundError(f"Card '{card_id}' found but has no ID.")
                return card.id

        raise NotFoundError(
            f"No card found with title '{card_id}'. Pass a card UUID for exact lookup."
        )


# =============================================================================
# Private Helpers
# =============================================================================


def _guess_mimetype(filename: str) -> str:
    """Guess MIME type from filename, defaulting to application/octet-stream."""
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or "application/octet-stream"
