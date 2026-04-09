"""Shared test fixtures for guru-sdk.

Provides a mock HttpClient via pytest-httpx and a pre-configured Guru client
that doesn't require real credentials.
"""

from __future__ import annotations

import pytest

from guru_sdk.http import HttpClient

# =============================================================================
# Clear proxy env vars — sandbox has SOCKS/HTTP proxies that break httpx
# =============================================================================

_PROXY_VARS = [
    "HTTP_PROXY", "http_proxy",
    "HTTPS_PROXY", "https_proxy",
    "ALL_PROXY", "all_proxy",
    "FTP_PROXY", "ftp_proxy",
    "GRPC_PROXY", "grpc_proxy",
    "RSYNC_PROXY",
]


@pytest.fixture(autouse=True)
def _clear_proxy_env(monkeypatch):  # type: ignore[no-untyped-def]
    """Remove proxy env vars so httpx doesn't try to use SOCKS."""
    for var in _PROXY_VARS:
        monkeypatch.delenv(var, raising=False)


# =============================================================================
# HttpClient fixture — uses pytest-httpx mock transport
# =============================================================================


@pytest.fixture()
def http_client(httpx_mock):  # type: ignore[no-untyped-def]
    """An HttpClient wired to pytest-httpx's mock transport."""
    # pytest-httpx patches httpx at the transport level, so we create
    # the client *after* the fixture has installed its mock.
    return HttpClient(
        base_url="https://api.getguru.com/api/v1",
        username="test@example.com",
        api_token="test-token-123",
    )
