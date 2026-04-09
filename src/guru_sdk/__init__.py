"""guru-sdk — Modern Python SDK for the Guru API.

Usage::

    from guru_sdk import Guru

    g = Guru()  # reads GURU_USER + GURU_TOKEN from env
    card = g.cards.get("card-id")

Public API:
    Guru: Client facade — the main entry point.
    CardResource: Card operations (CRUD, verify, tags, comments, folders, collaborators).
    GuruModel: Base class for all Pydantic models.
    Errors: GuruError, GuruApiError, NotFoundError, AuthenticationError,
            ForbiddenError, RateLimitError, ValidationError.
"""

from guru_sdk._version import __version__
from guru_sdk.client import Guru
from guru_sdk.errors import (
    AuthenticationError,
    ForbiddenError,
    GuruApiError,
    GuruError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)
from guru_sdk.models._base import GuruModel
from guru_sdk.resources.cards import CardResource

__all__ = [
    "AuthenticationError",
    "CardResource",
    "ForbiddenError",
    "Guru",
    "GuruApiError",
    "GuruError",
    "GuruModel",
    "NotFoundError",
    "RateLimitError",
    "ValidationError",
    "__version__",
]
