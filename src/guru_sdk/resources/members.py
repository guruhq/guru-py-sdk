"""Member resource — list, get, invite, remove team members.

Members are users within a Guru team. They can be invited as CORE (full access)
users. Email addresses are used as the primary
identifier for member operations.

API surface mirrors guru-cli's MemberResource.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from guru_sdk._compat import validate_free_text, validate_input
from guru_sdk.models._generated import TeamUser
from guru_sdk.resources._base import BaseResource

# =============================================================================
# Public API — MemberResource
# =============================================================================


class MemberResource(BaseResource):
    """Guru Members — list, get, invite, remove.

    Members are identified by email address. The invite method supports
    different user types.
    """

    # -------------------------------------------------------------------------
    # Read
    # -------------------------------------------------------------------------

    def list(self, *, search: str | None = None) -> list[TeamUser]:
        """List all team members, optionally filtered by search term.

        Args:
            search: Optional search string to filter members.
        """
        params: dict[str, str] = {}
        if search is not None:
            validate_free_text(search, "search")
            params["search"] = search
        return self._http.get_paginated("/members", TeamUser, **params)

    def get(self, email: str) -> TeamUser:
        """Get a single member by email address.

        Args:
            email: Member's email address.
        """
        validate_input(email, "email")
        # Percent-encode the email in the URL path (@ → %40)
        encoded_email = quote(email, safe="")
        return self._http.get(f"/members/{encoded_email}", TeamUser)

    # -------------------------------------------------------------------------
    # Write
    # -------------------------------------------------------------------------

    def invite(
        self,
        *,
        email: str,
        member_type: str = "CORE",
        message: str | None = None,
    ) -> None:
        """Invite a new member to the team.

        Args:
            email: Email address of the person to invite.
            member_type: User type — defaults to "CORE".
            message: Optional custom invitation message.
        """
        validate_input(email, "email")

        body: dict[str, Any] = {
            "emails": email,
            "teamMemberType": member_type,
        }
        if message is not None:
            validate_free_text(message, "message")
            body["customMessage"] = message

        self._http.post_no_content("/members/invite", body)

    def remove(self, email: str) -> None:
        """Remove a member from the team.

        Args:
            email: Email address of the member to remove.
        """
        validate_input(email, "email")
        encoded_email = quote(email, safe="")
        self._http.delete(f"/members/{encoded_email}")
