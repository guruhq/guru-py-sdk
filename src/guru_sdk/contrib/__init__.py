"""Higher-level utilities built on top of the core SDK.

Workflows: convenience functions that compose multiple resource calls.
Content: pure functions for working with card HTML content.
Publisher: folder-based content sync framework for external systems.
Bundle: zip-based content import for bulk card/folder creation.
"""

from guru_sdk.contrib.bundle import (
    Bundle,
    BundleNode,
    clean_html,
)
from guru_sdk.contrib.content import (
    find_urls,
    has_text,
    replace_text,
    replace_url,
)
from guru_sdk.contrib.publisher import (
    CardChanges,
    PublisherFolders,
)
from guru_sdk.contrib.workflows import (
    CardReplaceResult,
    add_tag_with_auto_create,
    add_user_to_groups,
    batch_add_users_to_group,
    dump_folder_hierarchy,
    make_collection_with_setup,
    move_card_between_folders,
    remove_user_from_groups,
    replace_text_in_collection_cards,
)

__all__ = [
    "Bundle",
    "BundleNode",
    "CardChanges",
    "CardReplaceResult",
    "PublisherFolders",
    "add_tag_with_auto_create",
    "add_user_to_groups",
    "batch_add_users_to_group",
    "clean_html",
    "dump_folder_hierarchy",
    "find_urls",
    "has_text",
    "make_collection_with_setup",
    "move_card_between_folders",
    "remove_user_from_groups",
    "replace_text",
    "replace_text_in_collection_cards",
    "replace_url",
]
