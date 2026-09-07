"""SQLAlchemy engine, declarative base, session factory, and schema helpers."""

from pathlib import Path

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "wasmbox-data"
DATA_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

DATABASE_PATH = DATA_DIR / "wasmbox.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"

Base = declarative_base()

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def ensure_schema() -> None:
    """
    Apply small, safe schema updates to the existing SQLite database.

    SQLAlchemy's create_all() creates missing tables, but it does not add
    new columns to tables that already exist. Day 2 adds the executions
    table's attack_type column, so this helper adds it when necessary.
    """

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    # The table will be created by Base.metadata.create_all() during startup.
    if "executions" not in table_names:
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("executions")
    }

    if "attack_type" not in existing_columns:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    ALTER TABLE executions
                    ADD COLUMN attack_type VARCHAR(64)
                    NOT NULL
                    DEFAULT 'none'
                    """
                )
            )