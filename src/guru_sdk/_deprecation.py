"""Deprecation utilities — built in from day one.

Every deprecated function emits a DeprecationWarning with:
- What to use instead
- When it will be removed

Warnings are visible in test output and logs. They survive for at least one
full minor version cycle and are only removed in major versions.
"""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

_F = TypeVar("_F", bound=Callable[..., Any])


def deprecated(*, removal_version: str, alternative: str) -> Callable[[_F], _F]:
    """Mark a function as deprecated with clear migration guidance.

    Args:
        removal_version: The version in which this will be removed (e.g. "2.0").
        alternative: What the caller should use instead (e.g. "g.cards.get()").

    Example::

        @deprecated(removal_version="2.0", alternative="g.cards.get()")
        def get_card(self, card_id: str) -> Card:
            return self.cards.get(card_id)
    """

    def decorator(func: _F) -> _F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{func.__qualname__}() is deprecated and will be removed in "
                f"guru-sdk {removal_version}. Use {alternative} instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
