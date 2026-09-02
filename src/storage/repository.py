"""Database helpers for execution records."""

from src.storage.db import SessionLocal
from src.storage.models import Execution


def record_execution_result(
    *,
    status: str,
    stdout: str = "",
    stderr: str = "",
    duration_ms: int = 0,
    artifact_id: str = "",
) -> None:
    """Store a completed sandbox execution."""

    with SessionLocal() as session:
        execution = Execution(
            status=status,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            artifact_id=artifact_id,
        )

        session.add(execution)
        session.commit()