"""Shared integration fixtures must only create and delete their own resources."""

from collections.abc import Generator
from types import SimpleNamespace
from typing import Any

import pytest

from integration import test_collection_config as config_tests
from integration import test_tokenize as tokenize_tests


class CollectionRegistry:
    """In-memory server boundary for exercising the actual integration fixtures."""

    def __init__(self) -> None:
        self.resources = {"OtherWorker": SimpleNamespace(name="OtherWorker")}
        self.created: list[str] = []

    def delete(self, name: str) -> None:
        self.resources.pop(name, None)

    def delete_all(self) -> None:
        self.resources.clear()

    def create(self, name: str, **kwargs: Any) -> SimpleNamespace:
        if name in self.resources:
            raise ValueError(f"collection already exists: {name}")
        collection = SimpleNamespace(name=name)
        self.resources[name] = collection
        self.created.append(name)
        return collection

    def create_from_dict(self, config: dict[str, Any]) -> SimpleNamespace:
        return self.create(config["class"])

    def get(self, name: str) -> SimpleNamespace:
        return self.resources[name]

    def list_all(self, simple: bool = True) -> dict[str, Any]:
        config_type = (
            config_tests._CollectionConfigSimple if simple else config_tests._CollectionConfig
        )
        return {name: object.__new__(config_type) for name in self.resources}


def test_overlapping_recipe_fixtures_own_distinct_collections() -> None:
    registry = CollectionRegistry()
    client = SimpleNamespace(collections=registry)
    first_fixture: Generator[Any, None, None] = tokenize_tests.recipe_collection.__wrapped__(client)
    second_fixture: Generator[Any, None, None] = tokenize_tests.recipe_collection.__wrapped__(
        client
    )
    try:
        first = next(first_fixture)
        second = next(second_fixture)
        assert first.name != second.name
        assert registry.get(first.name) is first
        first_fixture.close()
        assert registry.get(second.name) is second
    finally:
        first_fixture.close()
        second_fixture.close()
    assert set(registry.resources) == {"OtherWorker"}


def test_config_client_preserves_other_workers_collections(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = CollectionRegistry()
    closed: list[bool] = []
    client = SimpleNamespace(collections=registry, close=lambda: closed.append(True))
    monkeypatch.setattr(config_tests.weaviate, "connect_to_local", lambda **kwargs: client)
    fixture = config_tests.client.__wrapped__()
    try:
        assert next(fixture) is client
        assert "OtherWorker" in registry.resources
        registry.create("CreatedByAnotherWorkerDuringTest")
    finally:
        fixture.close()
    assert set(registry.resources) == {"OtherWorker", "CreatedByAnotherWorkerDuringTest"}
    assert closed == [True]


def test_list_collection_test_owns_unique_resources() -> None:
    registry = CollectionRegistry()
    client = SimpleNamespace(collections=registry)
    config_tests.test_collections_list(client)
    config_tests.test_collections_list(client)
    assert len(registry.created) == 2
    assert len(set(registry.created)) == 2
    assert set(registry.resources) == {"OtherWorker"}


def test_list_collection_test_cleans_up_after_read_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    registry = CollectionRegistry()
    client = SimpleNamespace(collections=registry)

    def failed_read(*args: Any) -> None:
        raise RuntimeError("synthetic list failure")

    monkeypatch.setattr(registry, "list_all", failed_read)
    with pytest.raises(RuntimeError, match="synthetic list failure"):
        config_tests.test_collections_list(client)
    assert set(registry.resources) == {"OtherWorker"}
