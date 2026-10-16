"""Hierarchy rendering — turn a folder hierarchy CSV into a visual tree.

Pure functions: they read a CSV written by
:func:`guru_sdk.contrib.workflows.dump_folder_hierarchy` (with or without
``include_cards``) and make no API calls.

Usage::

    from guru_sdk.contrib import dump_folder_hierarchy, render_hierarchy

    csv_path = dump_folder_hierarchy(g, "Engineering", include_cards=True)
    print(render_hierarchy(csv_path))                                # text tree
    render_hierarchy(csv_path, format="mermaid", path="tree.md")     # Mermaid in Markdown
"""

from __future__ import annotations

import csv
import os

_FORMATS = ("text", "mermaid")
_TYPES = ("folder", "card")
_CSV_SUFFIX = "_folder_hierarchy.csv"


def render_hierarchy(
    csv_path: str,
    *,
    format: str = "text",
    root_name: str | None = None,
    path: str | None = None,
) -> str:
    """Render a hierarchy CSV as a text tree or a Mermaid mindmap.

    Args:
        csv_path: CSV written by ``dump_folder_hierarchy``. Both layouts are
            accepted: folders only, or typed rows from ``include_cards=True``.
        format: ``"text"`` for a ``tree``-style listing (folders marked 📁),
            or ``"mermaid"`` for a mindmap (folders as boxes, cards rounded).
        root_name: Label for the root node. Defaults to the CSV filename
            with any ``_folder_hierarchy.csv`` suffix removed.
        path: Also write the rendering to this file. A Mermaid rendering
            written to a ``.md`` file is wrapped in a ```` ```mermaid ```` fence
            so GitHub and editors display it as a diagram.

    Returns:
        The rendered tree (Mermaid without the fence).
    """
    if format not in _FORMATS:
        raise ValueError(f"format must be one of {_FORMATS}, got {format!r}")

    rows = _read_rows(csv_path)
    root = root_name if root_name is not None else _default_root_name(csv_path)
    rendered = _render_text(rows, root) if format == "text" else _render_mermaid(rows, root)

    if path is not None:
        body = rendered
        if format == "mermaid" and path.lower().endswith(".md"):
            body = f"```mermaid\n{rendered}\n```"
        with open(path, "w", encoding="utf-8") as f:
            f.write(body + "\n")

    return rendered


def _read_rows(csv_path: str) -> list[tuple[str, list[str]]]:
    """Read the CSV as (type, path) pairs, detecting the folders-only layout.

    Typed rows always have a type plus at least one path cell. A folders-only
    CSV always starts with a top-level folder (a one-cell row), so any
    one-cell row means there is no type column.
    """
    with open(csv_path, newline="", encoding="utf-8") as f:
        raw = [row for row in csv.reader(f) if row]

    typed = all(len(row) >= 2 and row[0] in _TYPES for row in raw)
    if typed:
        return [(row[0], row[1:]) for row in raw]
    return [("folder", row) for row in raw]


def _default_root_name(csv_path: str) -> str:
    name = os.path.basename(csv_path)
    if name.endswith(_CSV_SUFFIX):
        return name[: -len(_CSV_SUFFIX)]
    return os.path.splitext(name)[0]


def _render_text(rows: list[tuple[str, list[str]]], root: str) -> str:
    lines = [root]
    # ancestors_last[d] is True when the open node at depth d was its parent's last child
    ancestors_last: list[bool] = []
    for i, (kind, item_path) in enumerate(rows):
        depth = len(item_path) - 1
        last = _is_last_sibling(rows, i)
        ancestors_last[depth:] = [last]
        prefix = "".join("    " if done else "│   " for done in ancestors_last[:depth])
        icon = "📁 " if kind == "folder" else ""
        lines.append(f"{prefix}{'└── ' if last else '├── '}{icon}{item_path[-1]}")
    return "\n".join(lines)


def _is_last_sibling(rows: list[tuple[str, list[str]]], index: int) -> bool:
    """True if no later row is a sibling before the parent's subtree ends."""
    item_path = rows[index][1]
    parent = item_path[:-1]
    for _, later in rows[index + 1 :]:
        if later[: len(parent)] != parent:
            return True
        if len(later) == len(item_path):
            return False
    return True


def _render_mermaid(rows: list[tuple[str, list[str]]], root: str) -> str:
    out = ["mindmap", f'  root(("{_mermaid_label(root)}"))']
    for kind, item_path in rows:
        label = _mermaid_label(item_path[-1])
        node = f'["{label}"]' if kind == "folder" else f'("{label}")'
        out.append("  " * (len(item_path) + 1) + node)
    return "\n".join(out)


def _mermaid_label(text: str) -> str:
    return text.replace('"', "#quot;")
