"""Security monitoring API routes."""

from fastapi import APIRouter
from sqlalchemy import select

from src.storage.db import SessionLocal
from src.storage.models import Execution


router = APIRouter(prefix="/api/security", tags=["security"])


@router.get("/feed")
def get_security_feed() -> list[dict]:
    """Return recent executions for the security monitoring feed."""

    with SessionLocal() as session:
        executions = session.scalars(
            select(Execution)
            .order_by(Execution.created_at.desc())
            .limit(50)
        ).all()

        return [
            {
                "id": execution.id,
                "attack_type": execution.attack_type,
                "status": execution.status,
                "duration_ms": execution.duration_ms,
                "artifact_id": execution.artifact_id,
                "wasm_sha256": execution.wasm_sha256,
                "created_at": execution.created_at.isoformat(),
            }
            for execution in executions
        ]