"""Security monitoring API routes."""

from collections import Counter

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


@router.get("/stats")
def get_security_stats() -> dict:
    """Return security statistics for execution history."""

    with SessionLocal() as session:
        executions = session.scalars(
            select(Execution)
        ).all()

        total_executions = len(executions)

        safe_executions = sum(
            1
            for execution in executions
            if execution.attack_type == "none"
        )

        detected_attacks = total_executions - safe_executions

        attack_counts = Counter(
            execution.attack_type
            for execution in executions
            if execution.attack_type != "none"
        )

        average_duration_ms = (
            sum(execution.duration_ms for execution in executions)
            / total_executions
            if total_executions
            else 0
        )

        return {
            "total_executions": total_executions,
            "safe_executions": safe_executions,
            "detected_attacks": detected_attacks,
            "attack_counts": dict(attack_counts),
            "average_duration_ms": round(average_duration_ms, 2),
        }