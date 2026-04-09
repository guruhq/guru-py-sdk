"""GuruModel — base class for all guru-sdk Pydantic models.

Design decisions:
- extra="ignore": Unknown API fields are silently dropped. This means an older
  SDK version talking to a newer API won't break — new fields are just invisible
  until the SDK is updated. Same pattern as Stripe, Twilio, OpenAI SDKs.

- populate_by_name=True: Accept both the JSON alias ("preferredPhrase") and the
  Pythonic field name ("title"). Makes the SDK usable from both raw API dicts
  and Python keyword arguments.

- frozen=True: Models are immutable. Mutating a model in-place creates a
  confusing situation where the local object disagrees with the server. Use
  resource methods (g.cards.update()) to mutate state — they return a fresh model.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class GuruModel(BaseModel):
    """Base for all guru-sdk models."""

    model_config = ConfigDict(
        extra="ignore",
        populate_by_name=True,
        frozen=True,
    )
