"""Pydantic v2 models for the Guru API.

All models inherit from GuruModel (extra="ignore", frozen=True) so they are
forward-compatible with API changes and immutable by default.
"""

from guru_sdk.models._base import GuruModel

__all__ = ["GuruModel"]
