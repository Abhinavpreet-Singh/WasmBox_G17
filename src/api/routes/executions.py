"""Execution history API routes."""

from fastapi import APIRouter
from sqlalchemy import select

from src.storage.db import SessionLocal
from src.storage.models import Execution


router = APIRouter(prefix="/api", tags=["executions"])


@router.get("/executions")
def get_executions() -> list[dict]:
    """Return execution history, newest first."""

    with SessionLocal() as session:
        executions = session.scalars(
            select(Execution).order_by(Execution.created_at.desc())
        ).all()

        return [
            {
                "id": execution.id,
                "artifact_id": execution.artifact_id,
                "status": execution.status,
                "stdout": execution.stdout,
                "stderr": execution.stderr,
                "duration_ms": execution.duration_ms,
                "wasm_sha256": execution.wasm_sha256,
                "created_at": execution.created_at.isoformat(),
            }
            for execution in executions
        ]