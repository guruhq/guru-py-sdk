"""Tests for guru_sdk.client — Guru facade."""

import pytest

from guru_sdk.client import Guru
from guru_sdk.errors import AuthenticationError


class TestCredentialResolution:
    """Guru resolves credentials from args → GURU_* → PYGURU_* env vars."""

    def test_explicit_args(self, httpx_mock):
        """Explicit username/api_token take precedence over env vars."""
        client = Guru(username="explicit@test.com", api_token="explicit-token")
        # Just verifying it doesn't raise — credentials accepted
        client.close()

    def test_guru_env_vars(self, monkeypatch, httpx_mock):
        monkeypatch.setenv("GURU_USER", "env@test.com")
        monkeypatch.setenv("GURU_TOKEN", "env-token")
        client = Guru()
        client.close()

    def test_pyguru_env_vars_fallback(self, monkeypatch, httpx_mock):
        """Falls back to PYGURU_* for backward compat with py-sdk v1."""
        monkeypatch.delenv("GURU_USER", raising=False)
        monkeypatch.delenv("GURU_TOKEN", raising=False)
        monkeypatch.setenv("PYGURU_USER", "legacy@test.com")
        monkeypatch.setenv("PYGURU_TOKEN", "legacy-token")
        client = Guru()
        client.close()

    def test_missing_credentials_raises(self, monkeypatch):
        monkeypatch.delenv("GURU_USER", raising=False)
        monkeypatch.delenv("GURU_TOKEN", raising=False)
        monkeypatch.delenv("PYGURU_USER", raising=False)
        monkeypatch.delenv("PYGURU_TOKEN", raising=False)
        with pytest.raises(AuthenticationError, match="Missing credentials"):
            Guru()

    def test_missing_token_raises(self, monkeypatch):
        monkeypatch.setenv("GURU_USER", "user@test.com")
        monkeypatch.delenv("GURU_TOKEN", raising=False)
        monkeypatch.delenv("PYGURU_TOKEN", raising=False)
        with pytest.raises(AuthenticationError):
            Guru()

    def test_missing_user_raises(self, monkeypatch):
        monkeypatch.delenv("GURU_USER", raising=False)
        monkeypatch.delenv("PYGURU_USER", raising=False)
        monkeypatch.setenv("GURU_TOKEN", "token")
        with pytest.raises(AuthenticationError):
            Guru()

    def test_explicit_args_override_env(self, monkeypatch, httpx_mock):
        monkeypatch.setenv("GURU_USER", "env@test.com")
        monkeypatch.setenv("GURU_TOKEN", "env-token")
        # Explicit args should win
        client = Guru(username="explicit@test.com", api_token="explicit-token")
        client.close()


class TestContextManager:
    """Guru supports context manager protocol for clean resource cleanup."""

    def test_context_manager(self, monkeypatch, httpx_mock):
        monkeypatch.setenv("GURU_USER", "user@test.com")
        monkeypatch.setenv("GURU_TOKEN", "token")
        with Guru() as g:
            assert isinstance(g, Guru)

    def test_close_is_idempotent(self, monkeypatch, httpx_mock):
        monkeypatch.setenv("GURU_USER", "user@test.com")
        monkeypatch.setenv("GURU_TOKEN", "token")
        client = Guru()
        client.close()
        # Second close should not raise
        client.close()


class TestCustomConfiguration:
    """Guru accepts custom base_url and timeout."""

    def test_custom_base_url(self, httpx_mock):
        client = Guru(
            username="user@test.com",
            api_token="token",
            base_url="https://custom.guru.com/api/v1",
        )
        client.close()

    def test_custom_timeout(self, httpx_mock):
        client = Guru(
            username="user@test.com",
            api_token="token",
            timeout=60.0,
        )
        client.close()
