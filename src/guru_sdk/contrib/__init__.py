"""Higher-level utilities built on top of the core SDK.

Workflows: convenience functions that compose multiple resource calls.
Publisher: folder-based content sync from a local directory to Guru (future).
Bundle: export a collection's cards and metadata to a local directory (future).
"""

from guru_sdk.contrib.workflows import (
    add_tag_with_auto_create,
    add_user_to_groups,
    batch_add_users_to_group,
    make_collection_with_setup,
    move_card_between_folders,
    remove_user_from_groups,
)

__all__ = [
    "add_tag_with_auto_create",
    "add_user_to_groups",
    "batch_add_users_to_group",
    "make_collection_with_setup",
    "move_card_between_folders",
    "remove_user_from_groups",
]
