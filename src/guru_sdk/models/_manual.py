"""Manually defined models for internal API endpoints.

These models cover resources that are NOT in the Guru public Swagger spec
(pages, page drafts, page permissions, page draft collaborators). They are
used by the internal API endpoints documented in guru-cli's ADR-014. They
also cover public endpoints whose live payload carries fields the spec
omits (FolderItemDetail).

Unlike _generated.py, these models are hand-written. They follow the same
conventions: GuruModel base class, snake_case fields with camelCase aliases,
all fields optional (API may omit any field).
"""

from __future__ import annotations

from typing import Annotated

from pydantic import AwareDatetime, Field

from guru_sdk.models._base import GuruModel
from guru_sdk.models._generated import FolderItem, Team, User, UserGroup

# =============================================================================
# Page Draft — response model for /pagedrafts endpoints
# =============================================================================


class PageDraft(GuruModel):
    """A page draft — an unpublished page edit.

    Similar to Page but includes page_id (link to the published page) and
    created_by (the user who created the draft). These fields are not on the
    generated Page model because page drafts are internal API only.
    """

    id: str | None = None
    page_id: Annotated[
        str | None, Field(alias="pageId", description="ID of the published page this draft is for")
    ] = None
    title: str | None = None
    json_content: Annotated[
        str | None, Field(alias="jsonContent", description="The JSON content of the page draft")
    ] = None
    hero_image: Annotated[
        str | None, Field(alias="heroImage", description="The hero image link")
    ] = None
    badge_emoji: Annotated[
        str | None, Field(alias="badgeEmoji", description="Emoji badge for the page draft")
    ] = None
    parent_page_id: Annotated[
        str | None, Field(alias="parentPageId", description="ID of the parent page")
    ] = None
    knowledge_agent_id: Annotated[
        str | None,
        Field(alias="knowledgeAgentId", description="ID of the default Knowledge Agent"),
    ] = None
    draft: bool | None = None
    editable: bool | None = None
    only_navigable: Annotated[
        bool | None,
        Field(alias="onlyNavigable", description="Navigation-only page (no content)"),
    ] = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None
    last_modified: Annotated[AwareDatetime | None, Field(alias="lastModified")] = None
    last_modified_by: Annotated[User | None, Field(alias="lastModifiedBy")] = None
    created_by: Annotated[User | None, Field(alias="createdBy")] = None
    team: Team | None = None


# =============================================================================
# Page Permission — permission entry on a page
# =============================================================================


class PagePermission(GuruModel):
    """A permission entry on a page — user or user-group with a role.

    Returned by GET /pages/{id}/permissions. The type field indicates whether
    this permission is for an individual user or a user-group.
    """

    id: str | None = None
    type: str | None = None  # "user" or "user-group"
    permission_type: Annotated[
        str | None,
        Field(alias="permissionType", description="EDITOR or VIEWER"),
    ] = None
    # objectRole is a nested object in the API — keep as dict for flexibility
    object_role: Annotated[
        dict[str, str | None] | None,
        Field(alias="objectRole"),
    ] = None


# =============================================================================
# Page Draft Collaborator — collaborator on a page draft
# =============================================================================


class PageDraftCollaborator(GuruModel):
    """A collaborator on a page draft — user or user-group with a role.

    Returned by GET /pagedrafts/{id}/collaborators.
    """

    id: str | None = None
    type: str | None = None  # "user" or "user-group"
    object_role: Annotated[
        dict[str, str | None] | None,
        Field(alias="objectRole"),
    ] = None
    user: User | None = None
    group: Annotated[dict[str, str | None] | None, Field(None)] = None


# =============================================================================
# Draft Collaborator — collaborator on a card draft
# =============================================================================


class DraftCollaborator(GuruModel):
    """A collaborator on a card draft — a user or user-group with access.

    Returned by GET/POST /drafts/{id}/collaborators. Unlike PageDraftCollaborator,
    card draft collaborators have no objectRole; they carry a dateCreated instead.
    Mirrors guru-cli's DraftCollaborator shape.

    Card drafts use ``userGroup`` for the group object; page drafts use ``group``
    (different backends — ADR-014; don't converge). For a user-group collaborator
    the ``id`` *is* the group ID.
    """

    id: str | None = None
    type: str | None = None  # "user" or "user-group"
    user: User | None = None
    user_group: Annotated[UserGroup | None, Field(alias="userGroup")] = None
    date_created: Annotated[AwareDatetime | None, Field(alias="dateCreated")] = None


# =============================================================================
# Folder Item Detail — GET /folders/{id}/items as the live API returns it
# =============================================================================


class FolderItemDetail(FolderItem):
    """A folder item with the title fields the live API sends.

    The spec's ``FolderItem`` lists only ``id``, ``itemId`` and ``type``, but
    the default response (``cardDetail=BASIC``) also carries ``title`` on
    folders and ``preferredPhrase`` on cards (confirmed on QA). guru-cli reads
    the same fields. Subclassing keeps ``isinstance(item, FolderItem)`` true.
    """

    title: str | None = None
    preferred_phrase: Annotated[str | None, Field(alias="preferredPhrase")] = None
    # Folders only: how many cards the folder holds (live payload, not in spec)
    number_of_facts: Annotated[int | None, Field(alias="numberOfFacts")] = None
