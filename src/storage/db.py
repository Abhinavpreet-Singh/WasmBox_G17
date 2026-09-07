"""SQLAlchemy engine, declarative base, session factory, and schema helpers."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.storage.models import Base


DATABASE_URL = "postgresql+psycopg2://wasmbox:wasmbox@localhost:5433/wasmbox"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
