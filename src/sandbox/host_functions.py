"""Whitelisted host functions (db_query, http_fetch stubs)."""

from typing import Any


def db_query(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    """Stub database query for the sandbox fixture database."""
    return []


def http_fetch(url: str) -> dict[str, Any]:
    """Stub HTTP fetch host function."""
    return {"status": "stubbed", "url": url}