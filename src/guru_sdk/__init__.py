"""guru-sdk — Modern Python SDK for the Guru API.

Usage::

    from guru_sdk import Guru

    g = Guru()  # reads GURU_USER + GURU_TOKEN from env
    card = g.cards.get("card-id")
    folders = g.folders.list()
    collections = g.collections.list()

Public API:
    Guru: Client facade — the main entry point.
    CardResource, FolderResource, CollectionResource: Resource modules.
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
from guru_sdk.resources.collections import CollectionResource
from guru_sdk.resources.folders import FolderResource

__all__ = [
    "AuthenticationError",
    "CardResource",
    "CollectionResource",
    "FolderResource",
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
