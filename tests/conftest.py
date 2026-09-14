"""Pytest configuration for WasmBox tests."""

import pytest


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Database setup is handled only by tests that require the database."""
    yield