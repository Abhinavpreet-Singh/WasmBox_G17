"""Plugin CRUD API routes."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.sandbox.ast_guard import lint_source
from src.sandbox.compiler_client import (
    ARTIFACTS_DIR,
    CompilerError,
    compile_python,
    sha256_file,
)
from src.storage.db import SessionLocal
from src.storage.models import Plugin


router = APIRouter(prefix="/api/plugins", tags=["plugins"])


class PluginCreateRequest(BaseModel):
    name: str
    source: str


class PluginResponse(BaseModel):
    id: int
    name: str
    source: str
    sha256: str


class ArtifactResponse(BaseModel):
    artifact_id: str
    filename: str
    size_bytes: int
    sha256: str


def _find_artifact_by_sha256(sha256: str) -> Path | None:
    """Find a WASM artifact by its SHA-256 fingerprint."""
    if not ARTIFACTS_DIR.exists():
        return None

    for path in ARTIFACTS_DIR.glob("*.wasm"):
        if sha256_file(path) == sha256:
            return path

    return None


@router.get("", response_model=list[ArtifactResponse])
def list_plugins() -> list[ArtifactResponse]:
    """List compiled WASM artifacts and their metadata."""
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    artifacts: list[ArtifactResponse] = []

    for path in sorted(ARTIFACTS_DIR.glob("*.wasm")):
        artifacts.append(
            ArtifactResponse(
                artifact_id=path.stem,
                filename=path.name,
                size_bytes=path.stat().st_size,
                sha256=sha256_file(path),
            )
        )

    return artifacts


@router.post("", response_model=PluginResponse, status_code=201)
def create_plugin(body: PluginCreateRequest) -> PluginResponse:
    """Compile a plugin and persist its metadata."""
    violations = lint_source(body.source)

    if violations:
        raise HTTPException(
            status_code=400,
            detail="AST guard rejected source before compile",
        )

    with SessionLocal() as session:
        existing = (
            session.query(Plugin)
            .filter(Plugin.name == body.name)
            .first()
        )

        if existing:
            raise HTTPException(
                status_code=409,
                detail="A plugin with this name already exists",
            )

    try:
        artifact = compile_python(body.source)
    except CompilerError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    with SessionLocal() as session:
        plugin = Plugin(
            name=body.name,
            source=body.source,
            sha256=artifact.wasm_sha256,
        )

        session.add(plugin)
        session.commit()
        session.refresh(plugin)

        return PluginResponse(
            id=plugin.id,
            name=plugin.name,
            source=plugin.source,
            sha256=plugin.sha256,
        )


@router.delete("/{plugin_id}")
def delete_plugin(plugin_id: int) -> dict[str, str]:
    """Delete a plugin and its compiled WASM artifact."""
    with SessionLocal() as session:
        plugin = session.get(Plugin, plugin_id)

        if plugin is None:
            raise HTTPException(
                status_code=404,
                detail="Plugin not found",
            )

        artifact = _find_artifact_by_sha256(plugin.sha256)

        if artifact is not None:
            artifact.unlink()

        session.delete(plugin)
        session.commit()

    return {"message": "Plugin deleted successfully"}
