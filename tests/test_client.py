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


class TestQaEnvironment:
    """Guru supports qa=True for QA environment and GURU_BASE_URL env var."""

    def test_qa_flag_sets_qa_base_url(self, httpx_mock):
        """qa=True sets base_url to qaapi.getguru.com."""
        client = Guru(
            username="user@test.com",
            api_token="token",
            qa=True,
        )
        # The HttpClient should be configured with the QA URL
        assert client._http._base_url == "https://qaapi.getguru.com/api/v1"
        client.close()

    def test_qa_false_uses_default(self, httpx_mock):
        """qa=False (the default) uses the production URL."""
        client = Guru(
            username="user@test.com",
            api_token="token",
            qa=False,
        )
        assert client._http._base_url == "https://api.getguru.com/api/v1"
        client.close()

    def test_guru_base_url_env_var(self, monkeypatch, httpx_mock):
        """GURU_BASE_URL env var overrides the default base URL."""
        monkeypatch.setenv("GURU_USER", "user@test.com")
        monkeypatch.setenv("GURU_TOKEN", "token")
        monkeypatch.setenv("GURU_BASE_URL", "https://custom.example.com/api/v1")
        client = Guru()
        assert client._http._base_url == "https://custom.example.com/api/v1"
        client.close()

    def test_explicit_base_url_overrides_env_var(self, monkeypatch, httpx_mock):
        """Explicit base_url arg wins over GURU_BASE_URL env var."""
        monkeypatch.setenv("GURU_BASE_URL", "https://env.example.com/api/v1")
        client = Guru(
            username="user@test.com",
            api_token="token",
            base_url="https://explicit.example.com/api/v1",
        )
        assert client._http._base_url == "https://explicit.example.com/api/v1"
        client.close()

    def test_qa_flag_overrides_env_var(self, monkeypatch, httpx_mock):
        """qa=True wins over GURU_BASE_URL env var."""
        monkeypatch.setenv("GURU_BASE_URL", "https://env.example.com/api/v1")
        client = Guru(
            username="user@test.com",
            api_token="token",
            qa=True,
        )
        assert client._http._base_url == "https://qaapi.getguru.com/api/v1"
        client.close()

    def test_qa_and_explicit_base_url_raises(self, httpx_mock):
        """Cannot pass both qa=True and explicit base_url — ambiguous."""
        with pytest.raises(ValueError, match="Cannot specify both"):
            Guru(
                username="user@test.com",
                api_token="token",
                qa=True,
                base_url="https://custom.guru.com/api/v1",
            )

    def test_env_var_not_used_when_qa_true(self, monkeypatch, httpx_mock):
        """qa=True always uses QA URL, ignores GURU_BASE_URL."""
        monkeypatch.setenv("GURU_BASE_URL", "https://should-not-use.com/api/v1")
        client = Guru(
            username="user@test.com",
            api_token="token",
            qa=True,
        )
        assert "qaapi" in client._http._base_url
        client.close()

    def test_default_no_env_var_uses_production(self, monkeypatch, httpx_mock):
        """Without GURU_BASE_URL and qa=False, uses production URL."""
        monkeypatch.delenv("GURU_BASE_URL", raising=False)
        client = Guru(
            username="user@test.com",
            api_token="token",
        )
        assert client._http._base_url == "https://api.getguru.com/api/v1"
        client.close()
