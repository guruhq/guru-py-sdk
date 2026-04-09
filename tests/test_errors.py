"""Tests for guru_sdk.errors — exception hierarchy."""

import pytest

from guru_sdk.errors import (
    AuthenticationError,
    ForbiddenError,
    GuruApiError,
    GuruError,
    NotFoundError,
    RateLimitError,
    ValidationError,
)


class TestExceptionHierarchy:
    """All API errors are catchable as GuruApiError or GuruError."""

    def test_guru_api_error_is_guru_error(self):
        assert issubclass(GuruApiError, GuruError)

    def test_not_found_is_guru_api_error(self):
        assert issubclass(NotFoundError, GuruApiError)

    def test_auth_error_is_guru_api_error(self):
        assert issubclass(AuthenticationError, GuruApiError)

    def test_forbidden_is_guru_api_error(self):
        assert issubclass(ForbiddenError, GuruApiError)

    def test_rate_limit_is_guru_api_error(self):
        assert issubclass(RateLimitError, GuruApiError)

    def test_validation_error_is_guru_error(self):
        assert issubclass(ValidationError, GuruError)

    def test_validation_error_is_not_api_error(self):
        # ValidationError is client-side — not an API response error
        assert not issubclass(ValidationError, GuruApiError)


class TestGuruApiError:
    """GuruApiError parses response bodies into human-readable messages."""

    def test_dict_body_with_message_key(self):
        err = GuruApiError(400, {"message": "Card not found"})
        assert err.status_code == 400
        assert err.message == "Card not found"
        assert "[400]" in str(err)

    def test_dict_body_with_error_key(self):
        err = GuruApiError(500, {"error": "Internal server error"})
        assert err.message == "Internal server error"

    def test_dict_body_with_detail_key(self):
        err = GuruApiError(422, {"detail": "Validation failed"})
        assert err.message == "Validation failed"

    def test_string_body(self):
        err = GuruApiError(502, "Bad Gateway")
        assert err.message == "Bad Gateway"

    def test_empty_body(self):
        err = GuruApiError(500)
        assert err.message == "Unknown error"

    def test_none_body(self):
        err = GuruApiError(500, None)
        assert err.message == "Unknown error"


class TestStatusSpecificErrors:
    """Status-specific errors set the correct status code."""

    def test_auth_error_status(self):
        err = AuthenticationError()
        assert err.status_code == 401

    def test_forbidden_status(self):
        err = ForbiddenError()
        assert err.status_code == 403

    def test_not_found_status(self):
        err = NotFoundError()
        assert err.status_code == 404

    def test_rate_limit_status(self):
        err = RateLimitError()
        assert err.status_code == 429

    def test_auth_error_custom_body(self):
        err = AuthenticationError({"message": "Token expired"})
        assert err.message == "Token expired"
        assert err.status_code == 401


class TestExceptionCatching:
    """Verify that try/except patterns work as expected."""

    def test_catch_specific_then_generic(self):
        with pytest.raises(NotFoundError):
            raise NotFoundError("gone")

    def test_catch_as_api_error(self):
        with pytest.raises(GuruApiError):
            raise NotFoundError("gone")

    def test_catch_as_guru_error(self):
        with pytest.raises(GuruError):
            raise NotFoundError("gone")

    def test_validation_error_not_caught_as_api_error(self):
        with pytest.raises(ValidationError):
            raise ValidationError("bad input")

        # Confirm it does NOT match GuruApiError
        with pytest.raises(ValidationError):
            try:
                raise ValidationError("bad input")
            except GuruApiError:
                pytest.fail("ValidationError should not be caught as GuruApiError")
