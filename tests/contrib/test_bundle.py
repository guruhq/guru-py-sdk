"""Tests for contrib/bundle — zip-based content import."""

from __future__ import annotations

import zipfile
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest

if TYPE_CHECKING:
    from pathlib import Path

# =============================================================================
# Test Helpers
# =============================================================================


def _make_guru_mock() -> MagicMock:
    """Create a mock Guru client for Bundle tests."""
    g = MagicMock()
    g._http = MagicMock()
    g._http._base_url = "https://api.getguru.com/api/v1"
    g._http._client = MagicMock()
    return g


# =============================================================================
# BundleNode — Tree Structure
# =============================================================================


class TestBundleNodeTree:
    """BundleNode parent/child relationships."""

    def test_add_to_establishes_parent_child(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child = bundle.node(id="card1", title="Card", content="<p>Hello</p>")
        child.add_to(parent)

        assert "card1" in parent.children
        assert parent in child.parents

    def test_add_child_default_appends(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child1 = bundle.node(id="c1", title="Card 1")
        child2 = bundle.node(id="c2", title="Card 2")
        parent.add_child(child1)
        parent.add_child(child2)

        assert parent.children == ["c1", "c2"]

    def test_add_child_first(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child1 = bundle.node(id="c1", title="Card 1")
        child2 = bundle.node(id="c2", title="Card 2")
        parent.add_child(child1)
        parent.add_child(child2, first=True)

        assert parent.children == ["c2", "c1"]

    def test_add_child_after(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        c1 = bundle.node(id="c1", title="Card 1")
        c2 = bundle.node(id="c2", title="Card 2")
        c3 = bundle.node(id="c3", title="Card 3")
        parent.add_child(c1)
        parent.add_child(c2)
        parent.add_child(c3, after=c1)

        assert parent.children == ["c1", "c3", "c2"]

    def test_add_child_cycle_detection(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        a = bundle.node(id="a", title="A")
        b = bundle.node(id="b", title="B")
        c = bundle.node(id="c", title="C")
        b.add_to(a)
        c.add_to(b)

        with pytest.raises(RuntimeError, match="cycle"):
            a.add_to(c)

    def test_add_child_duplicate_is_noop(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child = bundle.node(id="c1", title="Card 1")
        parent.add_child(child)
        parent.add_child(child)  # duplicate — should be ignored

        assert parent.children == ["c1"]

    def test_detach_removes_from_all_parents(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        p1 = bundle.node(id="p1", title="Parent 1")
        p2 = bundle.node(id="p2", title="Parent 2")
        child = bundle.node(id="c1", title="Card 1")
        child.add_to(p1)
        child.add_to(p2)

        child.detach()

        assert "c1" not in p1.children
        assert "c1" not in p2.children
        assert child.parents == []

    def test_move_to(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        p1 = bundle.node(id="p1", title="Parent 1")
        p2 = bundle.node(id="p2", title="Parent 2")
        child = bundle.node(id="c1", title="Card 1")
        child.add_to(p1)
        child.move_to(p2)

        assert "c1" not in p1.children
        assert "c1" in p2.children
        assert child.parents == [p2]

    def test_ancestors(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        a = bundle.node(id="a", title="A")
        b = bundle.node(id="b", title="B")
        c = bundle.node(id="c", title="C")
        b.add_to(a)
        c.add_to(b)

        ancestors = c.ancestors()
        # b is direct parent, a is grandparent
        assert b in ancestors
        assert a in ancestors

    def test_get_children_recursively(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        root = bundle.node(id="root", title="Root")
        child = bundle.node(id="child", title="Child")
        grandchild = bundle.node(id="gc", title="Grandchild")
        child.add_to(root)
        grandchild.add_to(child)

        descendants = root.get_children_recursively()
        ids = [n.id for n in descendants]
        assert "child" in ids
        assert "gc" in ids


# =============================================================================
# BundleNode — YAML Generation
# =============================================================================


class TestBundleNodeYaml:
    """BundleNode make_yaml and write_files."""

    def test_card_yaml(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(
            id="card1",
            title="My Card",
            content="<p>Hello</p>",
            url="https://example.com/card1",
            tags=["tag1", "tag2"],
        )
        node.type = "CARD"

        yaml_str = node.make_yaml()
        assert "Title: My Card" in yaml_str
        assert "ExternalId: card1" in yaml_str
        assert "ExternalUrl: https://example.com/card1" in yaml_str
        assert "tag1" in yaml_str

    def test_folder_yaml(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        folder = bundle.node(id="folder1", title="My Folder")
        folder.type = "FOLDER"
        card = bundle.node(id="c1", title="Card", content="<p>Hi</p>")
        card.type = "CARD"
        card.add_to(folder)

        yaml_str = folder.make_yaml()
        assert "Title: My Folder" in yaml_str
        assert "ExternalId: folder1" in yaml_str
        assert "Items:" in yaml_str

    def test_card_yaml_no_url(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        node.type = "CARD"

        yaml_str = node.make_yaml()
        assert "ExternalUrl" not in yaml_str

    def test_card_yaml_no_tags(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        node.type = "CARD"

        yaml_str = node.make_yaml()
        assert "Tags" not in yaml_str


# =============================================================================
# clean_html — attribute whitelist + class filter
# =============================================================================


class TestCleanHtml:
    """HTML sanitization: attribute whitelist + ghq-* class filter."""

    def test_strips_unknown_attributes(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<div data-custom="x" onclick="evil()" style="color:red"><p>Hello</p></div>'
        result = clean_html(html)
        assert "data-custom" not in result
        assert "onclick" not in result
        assert 'style="color:red"' in result
        assert "<p>Hello</p>" in result

    def test_keeps_whitelisted_attributes(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<a href="https://example.com" target="_blank" rel="noopener" title="Link">Click</a>'
        result = clean_html(html)
        assert 'href="https://example.com"' in result
        assert 'target="_blank"' in result
        assert 'rel="noopener"' in result
        assert 'title="Link"' in result

    def test_keeps_image_attributes(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<img src="pic.jpg" alt="Photo" height="100" width="200" data-id="x">'
        result = clean_html(html)
        assert 'src="pic.jpg"' in result
        assert 'alt="Photo"' in result
        assert 'height="100"' in result
        assert 'width="200"' in result
        assert "data-id" not in result

    def test_keeps_ghq_data_attributes(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<div data-ghq-card-content-type="markdown" data-random="x">Content</div>'
        result = clean_html(html)
        assert 'data-ghq-card-content-type="markdown"' in result
        assert "data-random" not in result

    def test_filters_css_classes_to_ghq_only(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<div class="ghq-card-content foo bar ghq-markdown">Content</div>'
        result = clean_html(html)
        assert "ghq-card-content" in result
        assert "ghq-markdown" in result
        assert "foo" not in result
        assert "bar" not in result

    def test_removes_class_attr_if_no_ghq_classes(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<div class="foo bar">Content</div>'
        result = clean_html(html)
        assert "class=" not in result

    def test_keeps_start_attribute_on_ol(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        html = '<ol start="5"><li>Item</li></ol>'
        result = clean_html(html)
        assert 'start="5"' in result

    def test_empty_html_passthrough(self) -> None:
        from guru_sdk.contrib.bundle import clean_html

        assert clean_html("") == ""
        assert clean_html("<p>Plain text</p>") == "<p>Plain text</p>"


# =============================================================================
# Bundle — Node Management
# =============================================================================


class TestBundleNodeManagement:
    """Bundle node(), has_node, remove_node."""

    def test_node_creates_new(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(id="card1", title="Card")

        assert bundle.has_node("card1")
        assert node.title == "Card"

    def test_node_updates_existing(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Original")
        node = bundle.node(id="card1", title="Updated", content="<p>New</p>")

        assert node.title == "Updated"
        assert node.content == "<p>New</p>"
        assert len(bundle.nodes) == 1  # same node, not a duplicate

    def test_node_url_hashing(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(url="https://example.com/page1", title="Page")

        assert node.id  # should be an MD5 hash
        assert bundle.has_node(node.id)

    def test_node_title_truncation(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        long_title = "x" * 300
        node = bundle.node(id="card1", title=long_title)

        assert len(node.title) <= 200

    def test_remove_node(self) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child = bundle.node(id="card1", title="Card")
        child.add_to(parent)

        bundle.remove_node(child)

        assert not bundle.has_node("card1")
        assert "card1" not in parent.children


# =============================================================================
# Bundle — Type Assignment
# =============================================================================


class TestBundleTypeAssignment:
    """Auto type assignment during zip()."""

    def test_node_with_children_becomes_folder(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder")
        child = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        child.add_to(parent)

        bundle.zip(path=tmp_path)

        assert parent.type == "FOLDER"
        assert child.type == "CARD"

    def test_node_with_content_becomes_card(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        node = bundle.node(id="card1", title="Card", content="<p>Hello</p>")

        bundle.zip(path=tmp_path)

        assert node.type == "CARD"

    def test_folder_with_content_gets_child_card(self, tmp_path: Path) -> None:
        """A folder that also has content gets a structural child card inserted."""
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        parent = bundle.node(id="folder1", title="Folder", content="<p>Folder intro</p>")
        child = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        child.add_to(parent)

        bundle.zip(path=tmp_path)

        assert parent.type == "FOLDER"
        # A structural content card should have been inserted
        content_node_id = "folder1_content"
        assert bundle.has_node(content_node_id)
        content_node = bundle.node(content_node_id)
        assert content_node.type == "CARD"
        assert content_node_id in parent.children

    def test_depth_limit_removes_deep_folders(self, tmp_path: Path) -> None:
        """Folders at depth >= 3 are removed."""
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        # Build 4 levels deep: root -> l1 -> l2 -> l3 (l3 should be removed)
        root = bundle.node(id="root", title="Root")
        l1 = bundle.node(id="l1", title="Level 1")
        l2 = bundle.node(id="l2", title="Level 2")
        l3 = bundle.node(id="l3", title="Level 3")
        card_deep = bundle.node(id="deep_card", title="Deep Card", content="<p>Deep</p>")
        l1.add_to(root)
        l2.add_to(l1)
        l3.add_to(l2)
        card_deep.add_to(l3)

        bundle.zip(path=tmp_path)

        assert l3.removed is True

    def test_skip_empty_folders(self, tmp_path: Path) -> None:
        """Folders that have no children after type assignment are removed during YAML generation."""
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g, skip_empty_folders=True)
        # Create a folder with an explicit type but no card children
        root = bundle.node(id="root", title="Root")
        empty_folder = bundle.node(id="empty", title="Empty Folder", node_type="FOLDER")
        empty_folder.add_to(root)
        root_card = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        root_card.add_to(root)

        bundle.zip(path=tmp_path)

        # The empty folder should be removed during items list generation
        assert empty_folder.removed is True


# =============================================================================
# Bundle — Zip Generation
# =============================================================================


class TestBundleZip:
    """Zip file creation with proper structure."""

    def test_zip_creates_collection_yaml(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hello</p>")

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        assert zip_path.exists()

        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            assert "collection.yaml" in names

    def test_zip_contains_card_files(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hello</p>")

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            assert "cards/card1.yaml" in names
            assert "cards/card1.html" in names

    def test_zip_contains_folder_yaml(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        folder = bundle.node(id="folder1", title="Folder")
        card = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        card.add_to(folder)

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        with zipfile.ZipFile(zip_path) as zf:
            names = zf.namelist()
            assert "folders/folder1.yaml" in names

    def test_zip_card_html_content(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hello World</p>")

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        with zipfile.ZipFile(zip_path) as zf:
            html = zf.read("cards/card1.html").decode("utf-8")
            assert "<p>Hello World</p>" in html

    def test_zip_collection_yaml_structure(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        folder = bundle.node(id="folder1", title="My Folder")
        card = bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        card.add_to(folder)

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        with zipfile.ZipFile(zip_path) as zf:
            yaml_content = zf.read("collection.yaml").decode("utf-8")
            assert "Version: 2" in yaml_content
            assert "Items:" in yaml_content

    def test_zip_with_tags_in_collection(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>", tags=["api", "docs"])

        bundle.zip(path=tmp_path)

        zip_path = tmp_path / f"collection_{bundle.id}.zip"
        with zipfile.ZipFile(zip_path) as zf:
            yaml_content = zf.read("collection.yaml").decode("utf-8")
            assert "api" in yaml_content
            assert "docs" in yaml_content


# =============================================================================
# Bundle — Upload
# =============================================================================


class TestBundleUpload:
    """Upload zip to Guru via /app/ endpoints."""

    def test_upload_import(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        # Mock collection resolution
        mock_collection = MagicMock()
        mock_collection.id = "coll-uuid"
        g.collections.get.return_value = mock_collection

        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        bundle.zip(path=tmp_path)

        # Mock the upload POST
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "import-123"}
        g._http._client.post.return_value = mock_response

        bundle.upload(name="Test Collection")

        # Should have called POST with contentFile field
        g._http._client.post.assert_called_once()
        call_kwargs = g._http._client.post.call_args
        assert "contentupload" in str(call_kwargs)

    def test_upload_sync(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        mock_collection = MagicMock()
        mock_collection.id = "coll-uuid"
        g.collections.get.return_value = mock_collection

        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        bundle.zip(path=tmp_path)

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "sync-123"}
        g._http._client.post.return_value = mock_response

        bundle.upload(name="Test Collection", is_sync=True)

        call_kwargs = g._http._client.post.call_args
        assert "contentsyncupload" in str(call_kwargs)

    def test_upload_creates_collection_if_missing(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        # First call: collection not found (raises)
        from guru_sdk.errors import NotFoundError

        g.collections.get.side_effect = NotFoundError("not found")
        mock_new_collection = MagicMock()
        mock_new_collection.id = "new-coll-uuid"
        g.collections.create.return_value = mock_new_collection

        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        bundle.zip(path=tmp_path)

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "import-123"}
        g._http._client.post.return_value = mock_response

        bundle.upload(name="New Collection", color="#1B998B", desc="Test")

        g.collections.create.assert_called_once()

    def test_upload_by_collection_id(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        bundle.zip(path=tmp_path)

        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {"id": "import-123"}
        g._http._client.post.return_value = mock_response

        bundle.upload(collection_id="coll-uuid")

        # Should not try to resolve collection by name
        g.collections.get.assert_not_called()

    def test_upload_requires_name_or_collection_id(self, tmp_path: Path) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        bundle.node(id="card1", title="Card", content="<p>Hi</p>")
        bundle.zip(path=tmp_path)

        with pytest.raises(ValueError, match=r"collection_id.*required"):
            bundle.upload()


# =============================================================================
# Bundle — Print Tree
# =============================================================================


class TestBundlePrintTree:
    """Debug tree printing."""

    def test_print_tree(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        from guru_sdk.contrib.bundle import Bundle

        g = _make_guru_mock()
        bundle = Bundle(g)
        root = bundle.node(id="root", title="Root")
        child = bundle.node(id="child", title="Child Card", content="<p>Hi</p>")
        child.add_to(root)

        bundle.print_tree()

        captured = capsys.readouterr()
        assert "Root" in captured.out
        assert "Child Card" in captured.out
