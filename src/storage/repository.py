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
    wasm_sha256: str = "",
    attack_type: str = "none",
) -> None:
    """Store a completed sandbox execution.

    Args:
        status: Final execution status, such as ``ok``, ``error``,
            or ``blocked``.
        stdout: Standard output produced by the execution.
        stderr: Standard error produced by the execution.
        duration_ms: Execution duration in milliseconds.
        artifact_id: Compiled artifact identifier, if available.
        wasm_sha256: SHA-256 hash of the executed WASM artifact.
        attack_type: Security classification assigned to the submitted
            source code. Defaults to ``none`` for executions that do not
            originate from source code.
    """

    with SessionLocal() as session:
        execution = Execution(
            status=status,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            artifact_id=artifact_id,
            wasm_sha256=wasm_sha256,
            attack_type=attack_type,
        )

        session.add(execution)
        session.commit()