"""Database models for plugins, plugin versions, and executions."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.storage.db import Base


class Plugin(Base):
    """Stored plugin source and metadata."""

    __tablename__ = "plugins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    versions: Mapped[list["PluginVersion"]] = relationship(
        back_populates="plugin",
        cascade="all, delete-orphan",
    )


class PluginVersion(Base):
    """Version metadata for a stored plugin."""

    __tablename__ = "plugin_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plugin_id: Mapped[int] = mapped_column(
        ForeignKey("plugins.id"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    plugin: Mapped[Plugin] = relationship(back_populates="versions")


class Execution(Base):
    """Record for a sandbox execution."""

    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    artifact_id: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )