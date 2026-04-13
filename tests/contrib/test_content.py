"""Tests for guru_sdk.contrib.content — pure HTML content utilities.

TDD tests covering all three content functions:
- has_text — check if HTML contains a text string
- find_urls — extract all URLs from HTML src/href attributes
- replace_url — rewrite URLs in HTML content
"""

from __future__ import annotations

# =============================================================================
# Test Data — realistic card HTML snippets
# =============================================================================

SIMPLE_HTML = "<p>Welcome to Guru! Check out our knowledge base.</p>"

RICH_HTML = """
<div>
  <h1>Onboarding Guide</h1>
  <p>Visit <a href="https://app.getguru.com/collections/abc">the collection</a> for details.</p>
  <img src="https://cdn.getguru.com/images/logo.png" alt="Guru Logo">
  <iframe src="https://www.youtube.com/embed/abc123"></iframe>
  <p>Contact <a href="mailto:support@getguru.com">support</a> for help.</p>
</div>
"""

MARKDOWN_HTML = """
<div>
  <p>Some regular content</p>
  <pre><code>
  [Link text](https://example.com/docs)
  ![Image](https://example.com/img.png)
  </code></pre>
</div>
"""

MULTI_URL_HTML = """
<div>
  <a href="https://old.example.com/page1">Page 1</a>
  <a href="https://old.example.com/page2">Page 2</a>
  <img src="https://old.example.com/logo.png">
  <a href="https://keep.example.com/unchanged">Keep this</a>
</div>
"""


# =============================================================================
# has_text
# =============================================================================


class TestHasText:
    """has_text(html, text, case_sensitive, include_tags)."""

    def test_finds_text_in_paragraph(self) -> None:
        """Simple text match in paragraph content."""
        from guru_sdk.contrib.content import has_text

        assert has_text(SIMPLE_HTML, "knowledge base") is True

    def test_case_insensitive_by_default(self) -> None:
        """Default search is case-insensitive."""
        from guru_sdk.contrib.content import has_text

        assert has_text(SIMPLE_HTML, "GURU") is True
        assert has_text(SIMPLE_HTML, "guru") is True

    def test_case_sensitive_when_requested(self) -> None:
        """case_sensitive=True requires exact case match."""
        from guru_sdk.contrib.content import has_text

        assert has_text(SIMPLE_HTML, "Guru", case_sensitive=True) is True
        assert has_text(SIMPLE_HTML, "guru", case_sensitive=True) is False

    def test_not_found_returns_false(self) -> None:
        """Text not present → False."""
        from guru_sdk.contrib.content import has_text

        assert has_text(SIMPLE_HTML, "nonexistent phrase") is False

    def test_finds_text_in_nested_html(self) -> None:
        """Finds text inside nested elements."""
        from guru_sdk.contrib.content import has_text

        assert has_text(RICH_HTML, "Onboarding Guide") is True
        assert has_text(RICH_HTML, "the collection") is True

    def test_strips_html_tags(self) -> None:
        """Searches visible text, not raw HTML tags."""
        from guru_sdk.contrib.content import has_text

        # Should find text content, not tag names
        assert has_text("<p>Hello <strong>world</strong></p>", "Hello world") is True
        # Should not match tag attribute values in visible text search
        assert has_text('<a href="secret">link</a>', "link") is True

    def test_empty_html(self) -> None:
        """Empty HTML → False for any text search."""
        from guru_sdk.contrib.content import has_text

        assert has_text("", "anything") is False

    def test_empty_search_text(self) -> None:
        """Empty search text → True (empty string is in every string)."""
        from guru_sdk.contrib.content import has_text

        assert has_text(SIMPLE_HTML, "") is True


# =============================================================================
# find_urls
# =============================================================================


class TestFindUrls:
    """find_urls(html)."""

    def test_finds_href_urls(self) -> None:
        """Extracts URLs from href attributes."""
        from guru_sdk.contrib.content import find_urls

        urls = find_urls(RICH_HTML)
        assert "https://app.getguru.com/collections/abc" in urls

    def test_finds_src_urls(self) -> None:
        """Extracts URLs from src attributes."""
        from guru_sdk.contrib.content import find_urls

        urls = find_urls(RICH_HTML)
        assert "https://cdn.getguru.com/images/logo.png" in urls
        assert "https://www.youtube.com/embed/abc123" in urls

    def test_finds_mailto_urls(self) -> None:
        """Includes mailto: links."""
        from guru_sdk.contrib.content import find_urls

        urls = find_urls(RICH_HTML)
        assert "mailto:support@getguru.com" in urls

    def test_no_duplicates(self) -> None:
        """Duplicate URLs are deduplicated."""
        from guru_sdk.contrib.content import find_urls

        html = '<a href="https://x.com">A</a><a href="https://x.com">B</a>'
        urls = find_urls(html)
        assert urls.count("https://x.com") == 1

    def test_empty_html(self) -> None:
        """Empty HTML → empty list."""
        from guru_sdk.contrib.content import find_urls

        assert find_urls("") == []

    def test_no_urls(self) -> None:
        """HTML with no links/images → empty list."""
        from guru_sdk.contrib.content import find_urls

        assert find_urls("<p>Just text, no links.</p>") == []

    def test_multiple_url_types(self) -> None:
        """Finds all URL types (href, src) across multiple elements."""
        from guru_sdk.contrib.content import find_urls

        urls = find_urls(MULTI_URL_HTML)
        assert len(urls) == 4
        assert "https://old.example.com/page1" in urls
        assert "https://old.example.com/page2" in urls
        assert "https://old.example.com/logo.png" in urls
        assert "https://keep.example.com/unchanged" in urls


# =============================================================================
# replace_url
# =============================================================================


class TestReplaceUrl:
    """replace_url(html, old_url, new_url)."""

    def test_replaces_href(self) -> None:
        """Replaces URL in href attributes."""
        from guru_sdk.contrib.content import replace_url

        html = '<a href="https://old.com/page">Link</a>'
        result_html, modified = replace_url(html, "https://old.com/page", "https://new.com/page")
        assert modified is True
        assert "https://new.com/page" in result_html
        assert "https://old.com/page" not in result_html

    def test_replaces_src(self) -> None:
        """Replaces URL in src attributes."""
        from guru_sdk.contrib.content import replace_url

        html = '<img src="https://old.com/img.png">'
        result_html, modified = replace_url(html, "https://old.com/img.png", "https://new.com/img.png")
        assert modified is True
        assert "https://new.com/img.png" in result_html
        assert "https://old.com/img.png" not in result_html

    def test_replaces_all_occurrences(self) -> None:
        """Replaces every occurrence of the URL, not just the first."""
        from guru_sdk.contrib.content import replace_url

        result_html, modified = replace_url(
            MULTI_URL_HTML,
            "https://old.example.com",
            "https://new.example.com",
        )
        assert modified is True
        assert result_html.count("https://new.example.com") == 3
        assert "https://old.example.com" not in result_html
        # Unrelated URLs are untouched
        assert "https://keep.example.com/unchanged" in result_html

    def test_no_match_returns_unchanged(self) -> None:
        """If the URL isn't found, return the HTML unchanged."""
        from guru_sdk.contrib.content import replace_url

        result_html, modified = replace_url(SIMPLE_HTML, "https://no-match.com", "https://new.com")
        assert modified is False
        assert result_html == SIMPLE_HTML

    def test_returns_modified_flag(self) -> None:
        """Returns a tuple of (html, modified_bool)."""
        from guru_sdk.contrib.content import replace_url

        result = replace_url(
            '<a href="https://old.com">x</a>',
            "https://old.com",
            "https://new.com",
        )
        # Result should be a tuple (html, was_modified)
        assert isinstance(result, tuple)
        html_out, modified = result
        assert modified is True
        assert "https://new.com" in html_out

    def test_not_modified_flag(self) -> None:
        """Returns modified=False when no replacement was made."""
        from guru_sdk.contrib.content import replace_url

        result = replace_url(SIMPLE_HTML, "https://no-match.com", "https://new.com")
        assert isinstance(result, tuple)
        _, modified = result
        assert modified is False

    def test_partial_url_match(self) -> None:
        """Replaces partial URL matches (domain rewriting)."""
        from guru_sdk.contrib.content import replace_url

        html = '<a href="https://old.example.com/docs/page1">Docs</a>'
        result_html, modified = replace_url(
            html, "https://old.example.com", "https://new.example.com"
        )
        assert modified is True
        assert "https://new.example.com/docs/page1" in result_html
