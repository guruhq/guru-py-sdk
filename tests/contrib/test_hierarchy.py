"""Tests for guru_sdk.contrib.hierarchy — rendering hierarchy CSVs as trees.

render_hierarchy() reads a CSV written by dump_folder_hierarchy (with or
without include_cards) and renders it as a text tree or a Mermaid mindmap.
Pure function: no API calls.
"""

from __future__ import annotations

import csv
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

TYPED_ROWS = [
    ["card", "Welcome"],
    ["folder", "Guides"],
    ["folder", "Guides", "Setup"],
    ["card", "Guides", "Setup", "Install Steps"],
    ["card", "Guides", "Setup", "In Two Places"],
    ["folder", "Guides", "Advanced"],
    ["folder", "Reference"],
    ["card", "Reference", "In Two Places"],
]


def _write_csv(path: Path, rows: list[list[str]]) -> str:
    with open(path, "w", newline="", encoding="utf-8") as f:
        csv.writer(f, quoting=csv.QUOTE_ALL).writerows(rows)
    return str(path)


class TestRenderText:
    """format="text" — a `tree`-style listing."""

    def test_typed_csv_renders_tree_with_connectors(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS)

        assert render_hierarchy(csv_path, root_name="Eng") == (
            "Eng\n"
            "├── Welcome\n"
            "├── 📁 Guides\n"
            "│   ├── 📁 Setup\n"
            "│   │   ├── Install Steps\n"
            "│   │   └── In Two Places\n"
            "│   └── 📁 Advanced\n"
            "└── 📁 Reference\n"
            "    └── In Two Places"
        )

    def test_folders_only_csv_is_detected(self, tmp_path: Path) -> None:
        """A CSV from dump_folder_hierarchy without include_cards has no type column."""
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(
            tmp_path / "x.csv",
            [["Guides"], ["Guides", "Setup"], ["Reference"]],
        )

        assert render_hierarchy(csv_path, root_name="Eng") == (
            "Eng\n├── 📁 Guides\n│   └── 📁 Setup\n└── 📁 Reference"
        )

    def test_folder_named_like_a_type_in_folders_only_csv(self, tmp_path: Path) -> None:
        """A top-level folder titled "card" must not be mistaken for a type column."""
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", [["card"], ["card", "folder"]])

        assert render_hierarchy(csv_path, root_name="R") == ("R\n└── 📁 card\n    └── 📁 folder")

    def test_empty_csv_renders_root_only(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", [])

        assert render_hierarchy(csv_path, root_name="Empty") == "Empty"

    def test_root_name_defaults_to_csv_filename(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "Engineering_folder_hierarchy.csv", [])

        assert render_hierarchy(csv_path) == "Engineering"


class TestRenderMermaid:
    """format="mermaid" — a Mermaid mindmap."""

    def test_folders_are_boxes_and_cards_are_rounded(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS[:4])

        assert render_hierarchy(csv_path, format="mermaid", root_name="Eng") == (
            "mindmap\n"
            '  root(("Eng"))\n'
            '    ("Welcome")\n'
            '    ["Guides"]\n'
            '      ["Setup"]\n'
            '        ("Install Steps")'
        )

    def test_double_quotes_in_titles_are_escaped(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", [["card", 'The "Big" One']])

        out = render_hierarchy(csv_path, format="mermaid", root_name="R")

        assert '("The #quot;Big#quot; One")' in out


class TestOutputFile:
    """path= writes the rendering to disk as well as returning it."""

    def test_text_written_to_path(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS)
        out_path = tmp_path / "tree.txt"

        result = render_hierarchy(csv_path, root_name="Eng", path=str(out_path))

        assert out_path.read_text(encoding="utf-8") == result + "\n"

    def test_mermaid_to_markdown_file_is_fenced(self, tmp_path: Path) -> None:
        """A .md target gets a ```mermaid fence so GitHub and editors render it."""
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS)
        out_path = tmp_path / "tree.md"

        result = render_hierarchy(csv_path, format="mermaid", root_name="Eng", path=str(out_path))

        assert not result.startswith("```")
        assert out_path.read_text(encoding="utf-8") == f"```mermaid\n{result}\n```\n"

    def test_mermaid_to_non_markdown_file_is_raw(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS)
        out_path = tmp_path / "tree.mmd"

        result = render_hierarchy(csv_path, format="mermaid", root_name="Eng", path=str(out_path))

        assert out_path.read_text(encoding="utf-8") == result + "\n"


class TestValidation:
    def test_unknown_format_raises(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.hierarchy import render_hierarchy

        csv_path = _write_csv(tmp_path / "x.csv", TYPED_ROWS)

        with pytest.raises(ValueError, match="format"):
            render_hierarchy(csv_path, format="svg")
