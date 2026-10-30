"""Scope release announcements away from real-server integration contracts."""

from typing import Any

import httpx
import pytest

from weaviate.connect import v4


def mock_current_release_feed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Return installed-version metadata only for the release-feed HTTP response."""
    original_send = httpx.Client.send
    original_async_send = httpx.AsyncClient.send

    def send(self: httpx.Client, request: httpx.Request, **kwargs: Any) -> httpx.Response:
        if request.method == "GET" and str(request.url) == v4.PYPI_PACKAGE_URL:
            return httpx.Response(
                200, json={"info": {"version": v4.client_version}}, request=request
            )
        return original_send(self, request, **kwargs)

    async def async_send(
        self: httpx.AsyncClient, request: httpx.Request, **kwargs: Any
    ) -> httpx.Response:
        if request.method == "GET" and str(request.url) == v4.PYPI_PACKAGE_URL:
            return httpx.Response(
                200, json={"info": {"version": v4.client_version}}, request=request
            )
        return await original_async_send(self, request, **kwargs)

    monkeypatch.setattr(httpx.Client, "send", send)
    monkeypatch.setattr(httpx.AsyncClient, "send", async_send)
