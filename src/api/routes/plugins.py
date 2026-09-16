"""Plugin registry API routes."""

import hashlib
from datetime import datetime
from src.api.routes.run import ExecutionResult, RunRequest, run_plugin

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from src.storage.db import SessionLocal
from src.storage.models import Plugin, PluginVersion

router = APIRouter(prefix="/api/plugins", tags=["plugins"])

class PluginSaveRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    source: str = Field(min_length=1)


class PluginResponse(BaseModel):
    id: int
    name: str
    source: str
    sha256: str
    latest_version: int
    created_at: datetime


def plugin_response(plugin: Plugin) -> PluginResponse:
    return PluginResponse(
        id=plugin.id,
        name=plugin.name,
        source=plugin.source,
        sha256=plugin.sha256,
        latest_version=max(
            (version.version for version in plugin.versions),
            default=0,
        ),
        created_at=plugin.created_at,
    )


@router.post("", response_model=PluginResponse)
def save_plugin(body: PluginSaveRequest) -> PluginResponse:
    """Create a plugin or save a new version under an existing name."""

    name = body.name.strip()
    source = body.source
    sha256 = hashlib.sha256(source.encode("utf-8")).hexdigest()

    with SessionLocal() as session:
        plugin = session.scalar(
            select(Plugin).where(Plugin.name == name)
        )

        if plugin is None:
            plugin = Plugin(
                name=name,
                source=source,
                sha256=sha256,
            )
            session.add(plugin)
            session.flush()
            next_version = 1
        else:
            plugin.source = source
            plugin.sha256 = sha256
            next_version = max(
                (version.version for version in plugin.versions),
                default=0,
            ) + 1

        plugin.versions.append(
            PluginVersion(
                version=next_version,
                sha256=sha256,
            )
        )

        session.commit()
        session.refresh(plugin)

        return plugin_response(plugin)


@router.get("", response_model=list[PluginResponse])
def list_plugins() -> list[PluginResponse]:
    """Return saved plugins newest first."""

    with SessionLocal() as session:
        plugins = session.scalars(
            select(Plugin).order_by(Plugin.created_at.desc())
        ).unique().all()

        return [plugin_response(plugin) for plugin in plugins]
class PluginVersionResponse(BaseModel):
    id: int
    plugin_id: int
    version: int
    sha256: str
    created_at: datetime


@router.get("/{plugin_id}/versions", response_model=list[PluginVersionResponse])
def list_plugin_versions(plugin_id: int) -> list[PluginVersionResponse]:
    """Return plugin versions newest first."""

    with SessionLocal() as session:
        plugin = session.get(Plugin, plugin_id)
        if plugin is None:
            raise HTTPException(status_code=404, detail="Plugin not found")

        versions = sorted(
            plugin.versions,
            key=lambda item: item.version,
            reverse=True,
        )

        return [
            PluginVersionResponse(
                id=version.id,
                plugin_id=version.plugin_id,
                version=version.version,
                sha256=version.sha256,
                created_at=version.created_at,
            )
            for version in versions
        ]


@router.post("/{plugin_id}/run", response_model=ExecutionResult)
def run_saved_plugin(plugin_id: int) -> ExecutionResult:
    """Compile and run the latest saved plugin source."""

    with SessionLocal() as session:
        plugin = session.get(Plugin, plugin_id)
        if plugin is None:
            raise HTTPException(status_code=404, detail="Plugin not found")

        source = plugin.source

    return run_plugin(RunRequest(source=source))
