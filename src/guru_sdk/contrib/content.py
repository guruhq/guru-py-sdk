"""Content utilities — pure functions for working with card HTML content.

These functions operate on raw HTML strings. They don't make API calls or
depend on any Guru models. Use them with card content, page content, or any
HTML string.

Usage::

    from guru_sdk.contrib.content import has_text, find_urls, replace_url

    if has_text(card.content, "deprecated"):
        print("Card mentions deprecated content")

    urls = find_urls(card.content)
    html, changed = replace_url(card.content, "old.com", "new.com")
"""

from __future__ import annotations

from html.parser import HTMLParser

# =============================================================================
# Text Search
# =============================================================================


def has_text(
    html: str,
    text: str,
    *,
    case_sensitive: bool = False,
) -> bool:
    """Check if HTML content contains a text string.

    Extracts visible text from the HTML (stripping tags) and searches
    for the given string. By default the search is case-insensitive.

    Args:
        html: Raw HTML string (e.g., card content).
        text: Text to search for.
        case_sensitive: If True, require exact case match.

    Returns:
        True if the text is found, False otherwise.
    """
    # Extract visible text by stripping all HTML tags
    visible = _extract_text(html)

    if case_sensitive:
        return text in visible
    return text.lower() in visible.lower()


# =============================================================================
# URL Extraction
# =============================================================================


def find_urls(html: str) -> list[str]:
    """Extract all URLs from src and href attributes in HTML.

    Finds URLs in <a href>, <img src>, <iframe src>, and any other
    element with src or href attributes. Results are deduplicated but
    order is preserved (first occurrence wins).

    Args:
        html: Raw HTML string.

    Returns:
        List of unique URL strings found in the HTML.
    """
    parser = _UrlExtractor()
    parser.feed(html)
    return parser.urls


# =============================================================================
# URL Replacement
# =============================================================================


def replace_url(
    html: str,
    old_url: str,
    new_url: str,
) -> tuple[str, bool]:
    """Replace all occurrences of a URL in HTML content.

    Performs a simple string replacement — works on both attribute values
    and inline text/markdown. Supports partial matches (e.g., replacing
    a domain prefix).

    Args:
        html: Raw HTML string.
        old_url: URL (or URL prefix) to find.
        new_url: Replacement URL.

    Returns:
        Tuple of (modified_html, was_modified). was_modified is True if
        any replacements were made.
    """
    if old_url not in html:
        return html, False

    modified = html.replace(old_url, new_url)
    return modified, True


# =============================================================================
# Private — HTML Text Extraction
# =============================================================================


class _TextExtractor(HTMLParser):
    """Minimal HTML parser that extracts visible text content."""

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []

    def handle_data(self, data: str) -> None:
        self._pieces.append(data)

    @property
    def text(self) -> str:
        return "".join(self._pieces)


def _extract_text(html: str) -> str:
    """Strip HTML tags and return visible text content."""
    parser = _TextExtractor()
    parser.feed(html)
    return parser.text


class _UrlExtractor(HTMLParser):
    """Minimal HTML parser that extracts URLs from src/href attributes."""

    def __init__(self) -> None:
        super().__init__()
        self._seen: set[str] = set()
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for attr_name, attr_value in attrs:
            if attr_name in ("src", "href") and attr_value is not None and attr_value not in self._seen:
                self._seen.add(attr_value)
                self.urls.append(attr_value)
