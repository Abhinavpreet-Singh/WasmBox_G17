"""WebSocket live execution stream."""

from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.metrics.prometheus import record_execution
from src.sandbox.ast_guard import lint_source
from src.sandbox.compiler_client import CompilerError, compile_python
from src.sandbox.extism_runtime import run_extism_artifact
from src.storage.repository import record_execution_result


router = APIRouter(tags=["websocket"])


@router.websocket("/ws/executions")
async def execution_stream(websocket: WebSocket) -> None:
    await websocket.accept()

    try:
        payload = await websocket.receive_json()
        source = payload.get("source", "")

        if not isinstance(source, str) or not source.strip():
            await websocket.send_json(
                {
                    "type": "done",
                    "status": "error",
                    "stdout": "",
                    "stderr": "Provide source code.",
                    "duration_ms": 0,
                    "message": "Provide source code.",
                }
            )
            return

        violations = lint_source(source)

        if violations:
            await websocket.send_json(
                {
                    "type": "done",
                    "status": "blocked",
                    "stdout": "",
                    "stderr": violations[0].message,
                    "duration_ms": 0,
                    "message": "AST guard rejected source before compile",
                    "violations": [
                        {
                            "line": violation.line,
                            "col": violation.col,
                            "message": violation.message,
                            "rule": violation.rule,
                        }
                        for violation in violations
                    ],
                }
            )

            record_execution_result(
                status="blocked",
                stdout="",
                stderr=violations[0].message,
                duration_ms=0,
                artifact_id="",
            )

            return

        try:
            compiled = compile_python(source)
        except CompilerError as exc:
            await websocket.send_json(
                {
                    "type": "done",
                    "status": "error",
                    "stdout": "",
                    "stderr": exc.log or str(exc),
                    "duration_ms": 0,
                    "message": str(exc),
                }
            )

            record_execution_result(
                status="error",
                stdout="",
                stderr=exc.log or str(exc),
                duration_ms=0,
                artifact_id="",
            )

            return

        await websocket.send_json(
            {
                "type": "compiled",
                "status": "ok",
                "artifact_id": compiled.artifact_id,
                "wasm_sha256": compiled.wasm_sha256,
                "compiler_log": compiled.compiler_log,
            }
        )

        # Count only executions that actually reach the WASM runtime.
        record_execution()

        result = run_extism_artifact(compiled.wasm_path)

        if result.stdout:
            await websocket.send_json(
                {
                    "type": "stdout",
                    "data": result.stdout,
                }
            )

        record_execution_result(
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            artifact_id=compiled.artifact_id,
        )

        await websocket.send_json(
            {
                "type": "done",
                "status": result.status,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_ms": result.duration_ms,
                "artifact": result.artifact,
                "artifact_id": compiled.artifact_id,
                "wasm_sha256": compiled.wasm_sha256,
                "message": "Compile and run complete",
            }
        )

    except WebSocketDisconnect:
        return

    except Exception as exc:  # noqa: BLE001
        try:
            await websocket.send_json(
                {
                    "type": "done",
                    "status": "error",
                    "stdout": "",
                    "stderr": str(exc),
                    "duration_ms": 0,
                    "message": "WebSocket execution failed",
                }
            )
        except Exception:
            pass