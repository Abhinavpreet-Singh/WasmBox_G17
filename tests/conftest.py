"""Pytest configuration — ensures the DB tables exist before any test that hits the DB."""

import pytest

from src.storage.db import engine
from src.storage.models import Base


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=engine)
    yield
