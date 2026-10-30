"""Release-feed isolation must preserve actual connection warning semantics."""

import asyncio
import warnings
from typing import Any

import httpx
import pytest

from test.package_version_feed import mock_current_release_feed
from weaviate.config import Timeout
from weaviate.connect import executor, v4
from weaviate.warnings import _Warnings

HOSTED_FORK_VERSION = "0.1.dev4832+gad17d415f"


def check_version(colour: executor.Colour) -> None:
    connection = object.__new__(v4._ConnectionBase)
    connection.timeout_config = Timeout()
    connection._client = None
    connection._grpc_channel = None
    if colour == "sync":
        executor.result(connection._check_package_version("sync"))
    else:
        asyncio.run(executor.aresult(connection._check_package_version("async")))


def synthetic_release_server(monkeypatch: pytest.MonkeyPatch, latest: str) -> list[str]:
    observed: list[str] = []

    def response(request: httpx.Request) -> httpx.Response:
        observed.append(str(request.url))
        return httpx.Response(200, json={"info": {"version": latest}}, request=request)

    def send(self: httpx.Client, request: httpx.Request, **kwargs: Any) -> httpx.Response:
        return response(request)

    async def asend(
        self: httpx.AsyncClient, request: httpx.Request, **kwargs: Any
    ) -> httpx.Response:
        return response(request)

    monkeypatch.setattr(httpx.Client, "send", send)
    monkeypatch.setattr(httpx.AsyncClient, "send", asend)
    return observed


@pytest.mark.parametrize("colour", ["sync", "async"])
@pytest.mark.parametrize("auth_warning", [False, True])
def test_current_feed_preserves_strict_connection_warning_counts(
    monkeypatch: pytest.MonkeyPatch, colour: executor.Colour, auth_warning: bool
) -> None:
    monkeypatch.setattr(v4, "client_version", HOSTED_FORK_VERSION)
    observed = synthetic_release_server(monkeypatch, "4.24.1")
    mock_current_release_feed(monkeypatch)
    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        check_version(colour)
        if auth_warning:
            _Warnings.auth_with_anon_weaviate()
    assert len(recorded) == int(auth_warning)
    if auth_warning:
        assert str(recorded[0].message).startswith("Auth001:")
    assert observed == [], "only the release-feed response should bypass its transport"


@pytest.mark.parametrize("colour", ["sync", "async"])
def test_stale_version_still_emits_exact_release_warning(
    monkeypatch: pytest.MonkeyPatch, colour: executor.Colour
) -> None:
    monkeypatch.setattr(v4, "client_version", HOSTED_FORK_VERSION)
    observed = synthetic_release_server(monkeypatch, "4.24.1")
    with pytest.warns(DeprecationWarning, match="Dep005:") as recorded:
        check_version(colour)
    assert len(recorded) == 1
    assert HOSTED_FORK_VERSION in str(recorded[0].message)
    assert "4.24.1" in str(recorded[0].message)
    assert observed == [v4.PYPI_PACKAGE_URL]


@pytest.mark.parametrize("colour", ["sync", "async"])
@pytest.mark.parametrize(
    "method,url", [("GET", "http://localhost:8080/v1/meta"), ("POST", v4.PYPI_PACKAGE_URL)]
)
def test_current_feed_forwards_other_http_requests(
    monkeypatch: pytest.MonkeyPatch, colour: executor.Colour, method: str, url: str
) -> None:
    observed = synthetic_release_server(monkeypatch, "real-transport")
    mock_current_release_feed(monkeypatch)
    if colour == "sync":
        with httpx.Client() as client:
            response = client.request(method, url, headers={"X-Test": "preserved"})
    else:

        async def request() -> httpx.Response:
            async with httpx.AsyncClient() as client:
                return await client.request(method, url, headers={"X-Test": "preserved"})

        response = asyncio.run(request())
    assert observed == [url]
    assert response.json() == {"info": {"version": "real-transport"}}
    assert response.request.headers["X-Test"] == "preserved"
    assert response.request.method == method
