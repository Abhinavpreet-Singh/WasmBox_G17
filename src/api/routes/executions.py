from fastapi import APIRouter
from sqlalchemy import select

from src.storage.db import SessionLocal
from src.storage.models import Execution


router = APIRouter(prefix="/api", tags=["executions"])


@router.get("/executions")
def get_violations() -> list[dict]:
    """Return execution records that finished with a non-ok status."""

    with SessionLocal() as session:
        executions = session.scalars(
            select(Execution)
            .where(Execution.status != "ok")
            .order_by(Execution.created_at.desc())
        ).all()

        return [
            {
                "id": execution.id,
                "status": execution.status,
                "stdout": execution.stdout,
                "stderr": execution.stderr,
                "duration_ms": execution.duration_ms,
                "artifact_id": execution.artifact_id,
                "created_at": execution.created_at.isoformat(),
            }
            for execution in executions
        ]