"""Zip-based content import — build a folder/card hierarchy and upload to Guru.

Customers build a tree of nodes (folders + cards with HTML content), the
Bundle generates a zip file in Guru's import format, and uploads it.

Usage::

    from guru_sdk import Guru
    from guru_sdk.contrib.bundle import Bundle

    g = Guru()
    bundle = Bundle(g)
    folder = bundle.node(id="folder1", title="Engineering Docs")
    card = bundle.node(id="card1", title="API Guide", content="<p>Hello</p>")
    card.add_to(folder)
    bundle.zip(path="/tmp/my_import")
    bundle.upload(name="Engineering")

Note: upload() uses the /app/contentupload endpoint which is not in the
public Swagger spec. See ADR-005 for rationale.
"""

from __future__ import annotations

import hashlib
import re
import time
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from guru_sdk.client import Guru

# =============================================================================
# Constants
# =============================================================================

FOLDER = "FOLDER"
CARD = "CARD"
MAX_FOLDER_DEPTH = 3

# Attributes that Guru's editor uses — strip everything else
_ATTR_WHITELIST = frozenset({
    "style",
    "start",     # numbered lists
    "href",      # links
    "target",
    "rel",
    "title",
    "src",       # images
    "alt",
    "height",
    "width",
    "class",     # guru elements
})

# data-ghq-* attributes are always kept (checked by prefix)
_DATA_GHQ_PREFIX = "data-ghq-"


# =============================================================================
# clean_html — Guru-specific attribute sanitization
# =============================================================================


def clean_html(html: str) -> str:
    """Sanitize HTML for Guru import: strip non-whitelisted attributes, keep ghq-* classes.

    Two focused operations:
    1. Remove all attributes except a whitelist (style, href, src, class, etc.)
       plus any data-ghq-* attributes.
    2. Filter CSS classes to only those prefixed with 'ghq-'.

    This does NOT do the heavy board-era HTML munging (table/list restructuring).
    Customers should pre-clean their HTML for structural issues.

    Args:
        html: Raw HTML string.

    Returns:
        Sanitized HTML string.
    """
    if not html:
        return html

    sanitizer = _HtmlSanitizer()
    sanitizer.feed(html)
    return sanitizer.result()


# =============================================================================
# BundleNode — tree node for import hierarchy
# =============================================================================


class BundleNode:
    """A node in the bundle's import tree — represents a folder or card.

    Nodes form a tree via parent/child relationships. During zip(), the
    Bundle auto-assigns types (FOLDER or CARD) based on structure.

    Args:
        id: Unique node identifier.
        bundle: Parent Bundle instance.
        url: Source URL (for external link tracking).
        title: Display title.
        desc: Description (folders only).
        content: HTML content (cards only).
        tags: List of tag strings.
        alt_urls: Alternative URLs that should resolve to this node.
        index: Sort order (lower = earlier).
        node_type: Explicit type override ("FOLDER" or "CARD").
    """

    def __init__(
        self,
        id: str,
        bundle: Bundle,
        *,
        url: str = "",
        title: str = "",
        desc: str = "",
        content: str = "",
        tags: list[str] | None = None,
        alt_urls: list[str] | None = None,
        index: int | None = None,
        node_type: str | None = None,
    ) -> None:
        self.id = id
        self.bundle = bundle
        self.url = url
        self.desc = desc
        self.title = title or id
        self.content = content
        self.children: list[str] = []
        self.parents: list[BundleNode] = []
        self.type = node_type
        self.tags = tags
        self.alt_urls = alt_urls
        self.removed = False
        self.index = 9999 if index is None else index

    # -------------------------------------------------------------------------
    # Public — Tree Manipulation
    # -------------------------------------------------------------------------

    def add_to(self, node: BundleNode) -> BundleNode:
        """Add this node as a child of the given parent node."""
        node.add_child(self)
        return self

    def add_child(
        self,
        child: BundleNode,
        *,
        first: bool = False,
        after: BundleNode | None = None,
    ) -> BundleNode:
        """Add a child node with optional ordering.

        By default children are appended. Use first=True to prepend, or
        after=<node> to insert after a specific sibling.

        Raises:
            RuntimeError: If adding this child would create a cycle.
        """
        # Cycle detection — check if child is already an ancestor of self
        for ancestor in self.ancestors():
            if ancestor.id == child.id:
                msg = (
                    f"adding '{child.title or child.id}' as a child of "
                    f"'{self.title or self.id}' would create a cycle"
                )
                raise RuntimeError(msg)

        # Duplicate check — silently skip
        if child.id in self.children:
            return self

        child.parents.append(self)
        if first:
            self.children.insert(0, child.id)
        elif after is not None:
            idx = self.children.index(after.id)
            self.children.insert(idx + 1, child.id)
        else:
            self.children.append(child.id)

        return self

    def detach(self) -> BundleNode:
        """Remove this node from all of its parents."""
        for parent in self.parents:
            if self.id in parent.children:
                parent.children.remove(self.id)
        self.parents = []
        return self

    def move_to(self, parent: BundleNode) -> BundleNode:
        """Detach from all parents and add to a new parent."""
        self.detach()
        parent.add_child(self)
        return self

    def ancestors(self) -> list[BundleNode]:
        """Return all ancestor nodes (breadth-first)."""
        result = self.parents[:]
        idx = 0
        while idx < len(result):
            result += result[idx].parents
            idx += 1
        return result

    def get_children_recursively(self) -> list[BundleNode]:
        """Return a flat list of all descendants."""
        all_children: list[BundleNode] = []
        for child_id in self.children:
            child = self.bundle.node(child_id)
            if not child.removed:
                all_children.append(child)
            all_children += child.get_children_recursively()
        return all_children

    # -------------------------------------------------------------------------
    # Public — YAML + HTML File Generation
    # -------------------------------------------------------------------------

    def make_yaml(self) -> str:
        """Generate YAML metadata for this node."""
        if self.removed:
            return ""

        if self.type == CARD:
            # Escape < in titles to prevent Guru rendering issues
            data: dict[str, Any] = {
                "Title": self.title.replace("<", "<\u200e"),
                "ExternalId": self.id,
            }
            if self.url:
                data["ExternalUrl"] = self.url
            if self.tags:
                data["Tags"] = self.tags
            return _to_yaml(data)

        if self.type == FOLDER:
            data = {
                "Title": self.title,
                "ExternalId": self.id,
                "Items": self._make_items_list(),
            }
            if self.url:
                data["ExternalUrl"] = self.url
            if self.desc:
                data["Description"] = self.desc
            return _to_yaml(data)

        return ""

    def write_files(self, base_path: Path) -> None:
        """Write YAML and HTML files for this node to disk."""
        if self.removed:
            return

        safe_id = self.id.replace("/", "_")

        if self.type == CARD:
            cards_dir = base_path / "cards"
            cards_dir.mkdir(parents=True, exist_ok=True)
            (cards_dir / f"{safe_id}.yaml").write_text(
                self.make_yaml(), encoding="utf-8"
            )
            (cards_dir / f"{safe_id}.html").write_text(
                self.content.strip() or "", encoding="utf-8"
            )
        elif self.type == FOLDER:
            folders_dir = base_path / "folders"
            folders_dir.mkdir(parents=True, exist_ok=True)
            (folders_dir / f"{safe_id}.yaml").write_text(
                self.make_yaml(), encoding="utf-8"
            )

    # -------------------------------------------------------------------------
    # Private — Items List for Folder YAML
    # -------------------------------------------------------------------------

    def _make_items_list(self) -> list[dict[str, Any]]:
        """Build the Items list for a folder's YAML file."""
        if self.removed:
            return []

        # Empty folder check
        if (
            not self.children
            and self.type == FOLDER
            and self.bundle.skip_empty_folders
        ):
            self.removed = True
            return []

        items: list[dict[str, Any]] = []
        for child_id in self.children:
            child_node = self.bundle.node(child_id)
            if child_node.removed:
                continue

            if child_node.type == CARD:
                items.append({"ID": child_node.id, "Type": "card"})
            elif child_node.type == FOLDER:
                folder_items = child_node._make_items_list()
                # Skip empty folders if configured
                if self.bundle.skip_empty_folders and not folder_items:
                    child_node.removed = True
                else:
                    items.append({
                        "ID": child_node.id,
                        "Type": "folder",
                        "Title": child_node.title,
                        "Items": folder_items,
                    })

        return items


# =============================================================================
# Bundle — orchestrator
# =============================================================================


class Bundle:
    """Build a zip-based content bundle for Guru import.

    Manages a tree of BundleNode objects, assigns types (folder vs card),
    generates YAML + HTML files, creates a zip archive, and uploads it.

    Args:
        g: Guru client instance.
        id: Bundle identifier (used in filenames). Defaults to a timestamp.
        skip_empty_folders: If True, omit folders with no children from the zip.
        silent: If True, suppress log output.
    """

    def __init__(
        self,
        g: Guru,
        id: str = "",
        *,
        skip_empty_folders: bool = False,
        silent: bool = False,
    ) -> None:
        self._g = g
        self.id = _slugify(id) if id else str(int(time.time()))
        self.nodes: list[BundleNode] = []
        self.resources: dict[str, str] = {}
        self.skip_empty_folders = skip_empty_folders
        self._silent = silent
        self.messages: list[dict[str, str]] = []
        self._zip_path: Path | None = None

    # -------------------------------------------------------------------------
    # Public — Node Management
    # -------------------------------------------------------------------------

    def node(
        self,
        id: str = "",
        *,
        url: str = "",
        title: str = "",
        content: str = "",
        desc: str = "",
        tags: list[str] | None = None,
        alt_urls: list[str] | None = None,
        index: int | None = None,
        node_type: str | None = None,
        sanitize_html: bool = True,
    ) -> BundleNode:
        """Create a new node or update an existing one.

        Nodes are identified by ID. If a URL is provided without an ID,
        the URL is hashed to create a stable ID. Calling node() with the
        same ID again updates the existing node's fields.

        Args:
            id: Unique identifier. If empty, derived from url.
            url: Source URL (optional, used for external link tracking).
            title: Display title (truncated to 200 chars).
            content: HTML content for cards.
            desc: Description (for folders).
            tags: List of tag strings.
            alt_urls: Alternative URLs for cross-node link matching.
            index: Sort order (lower = earlier).
            node_type: Explicit "FOLDER" or "CARD" override.
            sanitize_html: If True, run clean_html on content.

        Returns:
            The created or updated BundleNode.
        """
        node_id = str(id)
        if url and not node_id:
            # Hash the URL to create a stable ID (no extension)
            node_id = hashlib.md5(url.encode("utf-8")).hexdigest()
        elif node_id:
            # Sanitize: replace / with _ (not allowed in filenames)
            node_id = node_id.replace("/", "_")

        # Find existing node
        existing: BundleNode | None = None
        for n in self.nodes:
            if n.id == node_id:
                existing = n
                break

        # Truncate long titles
        if title:
            title = str(title).strip()
            if len(title) > 200:
                title = f"{title[0:197]}..."

        if not existing:
            existing = BundleNode(
                node_id,
                bundle=self,
                title=title,
                desc=desc,
                content=clean_html(content) if (content and sanitize_html) else content,
                tags=tags,
                alt_urls=alt_urls,
                index=index,
                node_type=node_type,
            )
            self.nodes.append(existing)
        else:
            # Update existing node's fields if new values provided
            if url:
                existing.url = url
            if title:
                existing.title = title
            if content:
                existing.content = (
                    clean_html(content) if sanitize_html else content
                )
            if node_type:
                existing.type = node_type
            if tags:
                existing.tags = tags
            if alt_urls:
                existing.alt_urls = alt_urls
            if index is not None:
                existing.index = index

        if url:
            existing.url = url

        return existing

    def has_node(self, id: str) -> bool:
        """Check if a node with the given ID exists."""
        return any(n.id == id for n in self.nodes)

    def remove_node(self, node: BundleNode) -> None:
        """Remove a node from the bundle and detach it from parents."""
        node.detach()
        if node in self.nodes:
            self.nodes.remove(node)

    # -------------------------------------------------------------------------
    # Public — Zip Generation
    # -------------------------------------------------------------------------

    def zip(self, *, path: Path | str | None = None) -> Path:
        """Finalize the bundle: assign types, write files, create zip.

        Steps:
        1. Sort nodes by index
        2. Assign types (FOLDER/CARD) based on tree structure
        3. Insert structural nodes (folder-with-content gets a child card)
        4. Write YAML + HTML files to disk
        5. Create zip archive

        Args:
            path: Directory to write files and zip into. Defaults to /tmp/.

        Returns:
            Path to the created zip file.
        """
        base_path = Path(path) if path else Path("/tmp")
        content_path = base_path / self.id
        content_path.mkdir(parents=True, exist_ok=True)

        # Sort nodes and their children by index
        self.nodes.sort(key=lambda n: n.index)
        for n in self.nodes:
            n.children.sort(key=lambda cid: self.node(cid).index)

        # Assign types via tree traversal
        _traverse_tree(self, _assign_types)

        # Insert structural nodes for folders-with-content
        _traverse_tree(self, _insert_nodes)

        # Remove nodes that got marked removed
        self.nodes = [n for n in self.nodes if not n.removed]

        # Write files for each node
        for n in self.nodes:
            n.write_files(content_path)

        # Write collection.yaml
        (content_path / "collection.yaml").write_text(
            self._make_collection_yaml(), encoding="utf-8"
        )

        # Build zip
        zip_path = base_path / f"collection_{self.id}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            for file_path in sorted(content_path.rglob("*")):
                if file_path.is_file() and not file_path.name.startswith("."):
                    arcname = str(file_path.relative_to(content_path))
                    zf.write(file_path, arcname)

        self._zip_path = zip_path
        self._log("zip", f"created {zip_path}")
        return zip_path

    # -------------------------------------------------------------------------
    # Public — Upload to Guru
    # -------------------------------------------------------------------------

    def upload(
        self,
        *,
        name: str = "",
        color: str = "",
        desc: str = "",
        collection_id: str = "",
        is_sync: bool = False,
    ) -> Any:
        """Upload the zip file to Guru.

        Uses the /app/contentupload (import) or /app/contentsyncupload (sync)
        endpoint. These are NOT in the public Swagger spec — see ADR-005.

        Import adds content to an existing collection. Sync replaces the
        entire collection's content.

        Args:
            name: Collection name. Creates the collection if it doesn't exist.
            color: Color for new collections (hex, e.g. "#1B998B").
            desc: Description for new collections.
            collection_id: Direct collection UUID (skips name resolution).
            is_sync: If True, use sync endpoint (replaces content).

        Returns:
            The JSON response from Guru's import endpoint.

        Raises:
            ValueError: If neither name nor collection_id is provided.
            RuntimeError: If zip() hasn't been called yet.
        """
        if self._zip_path is None:
            msg = "Call zip() before upload()"
            raise RuntimeError(msg)

        # Resolve collection
        if name and not collection_id:
            from guru_sdk.errors import NotFoundError

            try:
                collection = self._g.collections.get(name)
                collection_id = collection.id or ""
            except NotFoundError:
                # Create the collection
                collection = self._g.collections.create(
                    name=name, color=color or "#1B998B", description=desc
                )
                collection_id = collection.id or ""

        if not collection_id:
            msg = "Either name or collection_id is required"
            raise ValueError(msg)

        # Build the upload URL — /app/ route, not /api/v1/
        # base_url is like "https://api.getguru.com/api/v1"
        # We need "https://api.getguru.com/app/{route}?collectionId={id}"
        base = self._g._http._base_url
        # Strip /api/v1 (or similar) to get the host root
        host_root = re.sub(r"/api/v\d+/?$", "", base)
        route = "contentsyncupload" if is_sync else "contentupload"
        url = f"{host_root}/app/{route}?collectionId={collection_id}"

        # Multipart upload — different field names for import vs sync
        file_key = "file" if is_sync else "contentFile"
        filename = f"collection_{self.id}.zip"

        with open(self._zip_path, "rb") as f:
            files = {file_key: (filename, f, "application/zip")}
            response = self._g._http._client.post(url, files=files)

        # Use HttpClient's error handler
        self._g._http._raise_for_status(response)
        self._log("upload", f"{route} to collection {collection_id}")
        return response.json()

    # -------------------------------------------------------------------------
    # Public — Debug
    # -------------------------------------------------------------------------

    def print_tree(self) -> None:
        """Print the bundle hierarchy for debugging."""
        _traverse_tree(self, _print_node)

    # -------------------------------------------------------------------------
    # Private — Collection YAML
    # -------------------------------------------------------------------------

    def _make_collection_yaml(self) -> str:
        """Generate the collection.yaml content."""
        items: list[dict[str, str]] = []
        tags: list[str] = []

        for n in self.nodes:
            if n.removed:
                continue
            # Top-level folders (no parents) go in collection items
            if n.type == FOLDER and not n.parents:
                items.append({
                    "ID": n.id,
                    "Type": "folder",
                    "Title": n.title,
                })
            # Collect all unique tags from cards
            if n.type == CARD and n.tags:
                for tag in n.tags:
                    if tag not in tags:
                        tags.append(tag)

        data: dict[str, Any] = {
            "Version": 2,
            "Title": "Collection Title",
            "Items": items,
            "Tags": tags,
        }
        return _to_yaml(data)

    # -------------------------------------------------------------------------
    # Private — Logging
    # -------------------------------------------------------------------------

    def _log(self, *args: Any) -> None:
        """Internal log helper."""
        message = " ".join(str(a) for a in args)
        if not self._silent:
            print(message)
        self.messages.append({"type": "info", "message": message})


# =============================================================================
# Tree Traversal
# =============================================================================


def _traverse_tree(
    bundle: Bundle,
    func: Any,
    node: BundleNode | None = None,
    parent: BundleNode | None = None,
    depth: int = 0,
) -> None:
    """Walk the tree and apply func to each non-removed node."""
    if node is not None:
        if node.removed:
            return
        func(node, parent, depth)
        for child_id in node.children[:]:
            child = bundle.node(child_id)
            _traverse_tree(bundle, func, child, node, depth + 1)
    else:
        # Start from root nodes (no parents)
        for n in bundle.nodes:
            if not n.parents and not n.removed:
                _traverse_tree(bundle, func, n, depth=0)


def _assign_types(
    node: BundleNode,
    parent: BundleNode | None,
    depth: int,
) -> None:
    """Auto-assign FOLDER or CARD type based on structure."""
    if node.type is not None:
        return

    if node.children:
        if depth < MAX_FOLDER_DEPTH:
            node.type = FOLDER
        else:
            # Too deep — mark as removed
            _mark_removed(node)
    elif node.content:
        node.type = CARD
    else:
        node.type = CARD


def _insert_nodes(
    node: BundleNode,
    parent: BundleNode | None,
    depth: int,
) -> None:
    """If a FOLDER also has content, insert a child CARD to hold it."""
    if node.removed:
        return
    if node.content and node.type == FOLDER:
        content_id = f"{node.id}_content"
        content_node = node.bundle.node(
            id=content_id,
            url=node.url,
            title=node.title,
            content=node.content,
            alt_urls=node.alt_urls,
            node_type=CARD,
            sanitize_html=False,  # already sanitized
        )
        node.add_child(content_node, first=True)
        node.url = ""
        node.content = ""


def _mark_removed(node: BundleNode) -> None:
    """Recursively mark a node and all descendants as removed."""
    node.removed = True
    for parent in node.parents:
        if node.id in parent.children:
            parent.children.remove(node.id)
    for child_id in node.children:
        child = node.bundle.node(child_id)
        if node in child.parents:
            child.parents.remove(node)
        _mark_removed(child)


def _print_node(
    node: BundleNode,
    parent: BundleNode | None,
    depth: int,
) -> None:
    """Print a node for debugging."""
    indent = "  " * depth
    type_str = node.type or "?"
    if node.url:
        print(f"{indent}- {node.title or node.id} ({type_str}, url={node.url})")
    else:
        print(f"{indent}- {node.title or node.id} ({type_str})")


# =============================================================================
# HTML Sanitizer (stdlib html.parser)
# =============================================================================


class _HtmlSanitizer(HTMLParser):
    """Strip non-whitelisted attributes and filter CSS classes to ghq-* only.

    Uses stdlib html.parser — no BeautifulSoup dependency.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self._pieces: list[str] = []

    def result(self) -> str:
        return "".join(self._pieces)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        filtered = _filter_attrs(attrs)
        if filtered:
            attr_str = " ".join(
                f'{k}="{v}"' if v is not None else k for k, v in filtered
            )
            self._pieces.append(f"<{tag} {attr_str}>")
        else:
            self._pieces.append(f"<{tag}>")

    def handle_endtag(self, tag: str) -> None:
        self._pieces.append(f"</{tag}>")

    def handle_data(self, data: str) -> None:
        self._pieces.append(data)

    def handle_entityref(self, name: str) -> None:
        self._pieces.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._pieces.append(f"&#{name};")

    def handle_comment(self, data: str) -> None:
        self._pieces.append(f"<!--{data}-->")

    def handle_decl(self, decl: str) -> None:
        self._pieces.append(f"<!{decl}>")

    def handle_pi(self, data: str) -> None:
        self._pieces.append(f"<?{data}>")

    def unknown_decl(self, data: str) -> None:
        self._pieces.append(f"<![{data}]>")


def _filter_attrs(
    attrs: list[tuple[str, str | None]],
) -> list[tuple[str, str | None]]:
    """Filter attributes: keep whitelist + data-ghq-*, filter classes to ghq-*."""
    result: list[tuple[str, str | None]] = []

    for name, value in attrs:
        # Always keep data-ghq-* attributes
        if name.startswith(_DATA_GHQ_PREFIX):
            result.append((name, value))
            continue

        # Skip non-whitelisted attributes
        if name not in _ATTR_WHITELIST:
            continue

        # Special handling for class: keep only ghq-* classes
        if name == "class" and value is not None:
            classes = value.split()
            ghq_classes = [c for c in classes if c.startswith("ghq-")]
            if ghq_classes:
                result.append(("class", " ".join(ghq_classes)))
            # If no ghq- classes remain, drop the class attribute entirely
            continue

        result.append((name, value))

    return result


# =============================================================================
# YAML Serialization (minimal, no PyYAML dependency)
# =============================================================================


def _to_yaml(data: dict[str, Any], indent: int = 0) -> str:
    """Minimal YAML serializer for Guru's import format.

    Only supports the shapes needed: dicts, lists of dicts, lists of strings,
    and scalar values. No PyYAML dependency.
    """
    lines: list[str] = []
    prefix = "  " * indent

    for key, value in data.items():
        if isinstance(value, list):
            if not value:
                lines.append(f"{prefix}{key}: []")
            elif isinstance(value[0], dict):
                lines.append(f"{prefix}{key}:")
                for item in value:
                    # First key of item gets the - prefix
                    first = True
                    for k, v in item.items():
                        if first:
                            if isinstance(v, list):
                                lines.append(f"{prefix}- {k}:")
                                for sub_item in v:
                                    if isinstance(sub_item, dict):
                                        sub_first = True
                                        for sk, sv in sub_item.items():
                                            if sub_first:
                                                lines.append(f"{prefix}    - {sk}: {sv}")
                                                sub_first = False
                                            else:
                                                lines.append(f"{prefix}      {sk}: {sv}")
                                    else:
                                        lines.append(f"{prefix}    - {sub_item}")
                            else:
                                lines.append(f"{prefix}- {k}: {v}")
                            first = False
                        else:
                            if isinstance(v, list):
                                lines.append(f"{prefix}  {k}:")
                                for sub_item in v:
                                    if isinstance(sub_item, dict):
                                        sub_first = True
                                        for sk, sv in sub_item.items():
                                            if sub_first:
                                                lines.append(f"{prefix}    - {sk}: {sv}")
                                                sub_first = False
                                            else:
                                                lines.append(f"{prefix}      {sk}: {sv}")
                                    else:
                                        lines.append(f"{prefix}    - {sub_item}")
                            else:
                                lines.append(f"{prefix}  {k}: {v}")
            else:
                # List of scalars
                lines.append(f"{prefix}{key}:")
                for item in value:
                    lines.append(f"{prefix}- {item}")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(_to_yaml(value, indent + 1))
        else:
            lines.append(f"{prefix}{key}: {value}")

    return "\n".join(lines)


# =============================================================================
# Helpers
# =============================================================================


def _slugify(text: str) -> str:
    """Convert text to a filesystem-safe slug."""
    return re.sub(r"[^a-zA-Z0-9_\-]", "", text.replace(" ", "_"))
