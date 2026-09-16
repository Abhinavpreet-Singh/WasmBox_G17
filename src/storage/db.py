"""SQLAlchemy engine, declarative base, session factory, and schema helpers."""

import os

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from src.storage.models import Base


DATABASE_URL = os.environ.get(
    "WASMBOX_DATABASE_URL",
    "postgresql+psycopg2://wasmbox:wasmbox@localhost:5433/wasmbox",
)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=_connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def init_db() -> None:
    """Create database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)


def ensure_schema() -> None:
    """Add newer execution columns to an existing database."""

    init_db()

    inspector = inspect(engine)
    execution_columns = {
        column["name"]
        for column in inspector.get_columns("executions")
    }

    with engine.begin() as connection:
        if "wasm_sha256" not in execution_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE executions
                    ADD COLUMN wasm_sha256 VARCHAR(64)
                    NOT NULL DEFAULT ''
                    """
                )
            )

        if "attack_type" not in execution_columns:
            connection.execute(
                text(
                    """
                    ALTER TABLE executions
                    ADD COLUMN attack_type VARCHAR(100)
                    NOT NULL DEFAULT 'none'
                    """
                )
            )
