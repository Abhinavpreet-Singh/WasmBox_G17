"""Whitelisted host functions (db_query, http_fetch stubs)."""
from __future__ import annotations

import typing
from typing import Any

import extism

from src.sandbox.capabilities import Capability, CapabilitySet

# In-memory fixture "database" — never runs plugin-supplied SQL.
_FIXTURE_ROWS: dict[str, list[dict[str, Any]]] = {
    "users": [
        {"id": 1, "name": "Ada Lovelace"},
        {"id": 2, "name": "Grace Hopper"},
    ],
}


@extism.host_fn(name="db_query", namespace="wasmbox")
def db_query(query: str) -> typing.Annotated[list, extism.Json]:
    """Stub database query for the sandbox fixture database.

    `query` is treated as a fixture table name, never as SQL — this never
    executes plugin-supplied SQL.
    """
    return _FIXTURE_ROWS.get(query, [])


@extism.host_fn(name="http_fetch", namespace="wasmbox")
def http_fetch(url: str) -> typing.Annotated[dict, extism.Json]:
    """Stub HTTP fetch host function."""
    return {"status": "stubbed", "url": url}


def build_host_functions(capabilities: CapabilitySet | None) -> list:
    """Return only the host functions a CapabilitySet actually grants.

    An execution with no capabilities gets an empty list — the Extism plugin
    is instantiated with zero host functions, so it has no way to reach
    `db_query` or `http_fetch` no matter what the plugin's code tries.
    """
    capabilities = capabilities or CapabilitySet.none()
    functions = []
    if capabilities.has(Capability.ALLOW_DB_BRIDGE):
        functions.append(db_query)
    if capabilities.has(Capability.ALLOW_HTTP_FETCH):
        functions.append(http_fetch)
    return functions


def db_query(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Stub database query for the sandbox fixture database."""
    return []


def http_fetch(url: str) -> dict[str, Any]:
    """Stub HTTP fetch host function."""
    return {"status": "stubbed", "url": url}