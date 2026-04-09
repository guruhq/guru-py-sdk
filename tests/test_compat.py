"""Tests for guru_sdk._compat — ID detection and input validation."""

import pytest

from guru_sdk._compat import is_uuid, validate_free_text, validate_input
from guru_sdk.errors import ValidationError


class TestIsUuid:
    """UUID detection — standard v4 UUIDs."""

    def test_valid_lowercase(self):
        assert is_uuid("550e8400-e29b-41d4-a716-446655440000") is True

    def test_valid_uppercase(self):
        assert is_uuid("550E8400-E29B-41D4-A716-446655440000") is True

    def test_valid_mixed_case(self):
        assert is_uuid("550e8400-E29B-41d4-a716-446655440000") is True

    def test_not_uuid_plain_string(self):
        assert is_uuid("my-card-title") is False

    def test_not_uuid_too_short(self):
        assert is_uuid("550e8400") is False

    def test_not_uuid_missing_dashes(self):
        assert is_uuid("550e8400e29b41d4a716446655440000") is False

    def test_not_uuid_empty(self):
        assert is_uuid("") is False

    def test_not_uuid_with_extra_chars(self):
        assert is_uuid("550e8400-e29b-41d4-a716-446655440000-extra") is False


class TestValidateInput:
    """Strict validation for resource IDs and names."""

    def test_valid_uuid_passes(self):
        val = "550e8400-e29b-41d4-a716-446655440000"
        assert validate_input(val, "card ID") == val

    def test_valid_name_passes(self):
        assert validate_input("Engineering", "collection name") == "Engineering"

    def test_control_chars_rejected(self):
        with pytest.raises(ValidationError, match="control characters"):
            validate_input("bad\x00input", "card ID")

    def test_null_byte_rejected(self):
        with pytest.raises(ValidationError, match="control characters"):
            validate_input("id\x00", "card ID")

    def test_tab_allowed(self):
        # Tab (0x09) is explicitly allowed
        assert validate_input("has\ttab", "field") == "has\ttab"

    def test_newline_allowed(self):
        # Newline (0x0a) is explicitly allowed
        assert validate_input("has\nnewline", "field") == "has\nnewline"

    def test_path_traversal_rejected(self):
        with pytest.raises(ValidationError, match="path traversal"):
            validate_input("../../etc/passwd", "card ID")

    def test_path_traversal_backslash_rejected(self):
        with pytest.raises(ValidationError, match="path traversal"):
            validate_input("..\\windows\\system32", "card ID")

    def test_query_char_rejected(self):
        with pytest.raises(ValidationError, match="\\? or #"):
            validate_input("card-id?extra=1", "card ID")

    def test_fragment_char_rejected(self):
        with pytest.raises(ValidationError, match="\\? or #"):
            validate_input("card-id#section", "card ID")

    def test_percent_encoding_rejected(self):
        with pytest.raises(ValidationError, match="percent-encoded"):
            validate_input("card%20id", "card ID")

    def test_returns_value_on_success(self):
        result = validate_input("valid-id", "test")
        assert result == "valid-id"


class TestValidateFreeText:
    """Lenient validation for questions, search terms, comments."""

    def test_question_mark_allowed(self):
        text = "What is the onboarding process?"
        assert validate_free_text(text, "question") == text

    def test_hash_allowed(self):
        text = "Issue #123 summary"
        assert validate_free_text(text, "comment") == text

    def test_percent_encoding_allowed(self):
        text = "100% complete"
        assert validate_free_text(text, "comment") == text

    def test_path_traversal_allowed(self):
        # Free text may contain path-like strings in natural language
        text = "Navigate to ../docs for details"
        assert validate_free_text(text, "comment") == text

    def test_control_chars_still_rejected(self):
        with pytest.raises(ValidationError, match="control characters"):
            validate_free_text("bad\x00text", "search term")

    def test_returns_value_on_success(self):
        result = validate_free_text("search query", "search")
        assert result == "search query"
