"""WebSocket live execution stream."""

from __future__ import annotations

import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.metrics.prometheus import record_compile_error, record_execution
from src.sandbox.ast_guard import lint_source
from src.security.classifier import classify_source
from src.sandbox.compiler_client import CompilerError, compile_python
from src.sandbox.extism_runtime import run_extism_artifact
from src.sandbox.runtime import resolve_compiled_artifact, run_wasm
from src.storage.repository import record_execution_result

router = APIRouter(tags=["websocket"])


async def _send(ws: WebSocket, event: str, **payload) -> None:
    """Send a typed JSON frame over the WebSocket."""
    await ws.send_text(
        json.dumps(
            {
                "event": event,
                **payload,
            }
        )
    )


@router.websocket("/ws/executions")
async def ws_executions(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for live execution streaming.

    Client sends one JSON message per execution request:

      { "type": "run",  "source": "<python source>" }
      { "type": "run",  "artifact_id": "<id>" }
      { "type": "wasm", "artifact": "hello" }

    Server emits typed frames:

      { "event": "start", ... }
      { "event": "stdout", "chunk": "..." }
      {
          "event": "done",
          "status": "ok"|"error"|"blocked"|"timeout",
          "duration_ms": 0,
          "stderr": "...",
          "artifact": "...",
          "artifact_id": "...",
          "wasm_sha256": "...",
          "attack_type": "none"
      }
      { "event": "error", "detail": "..." }
    """

    await websocket.accept()

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _send(
                    websocket,
                    "error",
                    detail="Invalid JSON",
                )
                continue

            if not isinstance(msg, dict):
                await _send(
                    websocket,
                    "error",
                    detail="WebSocket message must be a JSON object",
                )
                continue

            msg_type = msg.get("type", "run")

            # ── Raw WASM execution ──────────────────────────────────────────
            if msg_type == "wasm":
                artifact = msg.get("artifact", "hello")
                stdin = msg.get("stdin", "")

                await _send(
                    websocket,
                    "start",
                    artifact=artifact,
                    attack_type="none",
                )

                try:
                    result = run_wasm(
                        artifact,
                        stdin=stdin,
                    )

                    if result.stdout:
                        await _send(
                            websocket,
                            "stdout",
                            chunk=result.stdout,
                        )

                    record_execution_result(
                        status=result.status,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        duration_ms=result.duration_ms,
                        artifact_id="",
                        wasm_sha256="",
                        attack_type="none",
                    )

                    await _send(
                        websocket,
                        "done",
                        status=result.status,
                        duration_ms=result.duration_ms,
                        stderr=result.stderr,
                        artifact=result.artifact,
                        artifact_id="",
                        wasm_sha256="",
                        attack_type="none",
                    )

                except (FileNotFoundError, ValueError) as exc:
                    await _send(
                        websocket,
                        "error",
                        detail=str(exc),
                    )

                continue

            # ── Existing compiled artifact execution ─────────────────────────
            if msg.get("artifact_id"):
                artifact_id = msg["artifact_id"]

                await _send(
                    websocket,
                    "start",
                    artifact_id=artifact_id,
                    attack_type="none",
                )

                try:
                    wasm_path = resolve_compiled_artifact(artifact_id)
                except (FileNotFoundError, ValueError) as exc:
                    await _send(
                        websocket,
                        "error",
                        detail=str(exc),
                    )
                    continue

                record_execution()

                result = run_extism_artifact(wasm_path)

                if result.stdout:
                    await _send(
                        websocket,
                        "stdout",
                        chunk=result.stdout,
                    )

                record_execution_result(
                    status=result.status,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration_ms=result.duration_ms,
                    artifact_id=artifact_id,
                    wasm_sha256="",
                    attack_type="none",
                )

                await _send(
                    websocket,
                    "done",
                    status=result.status,
                    duration_ms=result.duration_ms,
                    stderr=result.stderr,
                    artifact=result.artifact,
                    artifact_id=artifact_id,
                    wasm_sha256="",
                    attack_type="none",
                )

                continue

            # ── Compile and run source code ──────────────────────────────────
            source = msg.get("source", "").strip()

            if not source:
                await _send(
                    websocket,
                    "error",
                    detail="Provide source or artifact_id",
                )
                continue

            # Classify the source before AST validation and compilation.
            attack_type = classify_source(source)

            # AST guard
            violations = lint_source(source)

            if violations:
                reason = violations[0].message

                await _send(
                    websocket,
                    "done",
                    status="blocked",
                    duration_ms=0,
                    stderr=reason,
                    artifact="",
                    artifact_id="",
                    wasm_sha256="",
                    attack_type=attack_type,
                    violations=[
                        {
                            "line": violation.line,
                            "col": violation.col,
                            "rule": violation.rule,
                            "message": violation.message,
                        }
                        for violation in violations
                    ],
                )

                record_execution_result(
                    status="blocked",
                    stdout="",
                    stderr=reason,
                    duration_ms=0,
                    artifact_id="",
                    wasm_sha256="",
                    attack_type=attack_type,
                )

                continue

            await _send(
                websocket,
                "start",
                phase="compile",
                attack_type=attack_type,
            )

            try:
                compiled = compile_python(source)
            except CompilerError as exc:
                record_compile_error()

                reason = exc.log or str(exc)

                record_execution_result(
                    status="error",
                    stdout="",
                    stderr=reason,
                    duration_ms=0,
                    artifact_id="",
                    wasm_sha256="",
                    attack_type=attack_type,
                )

                await _send(
                    websocket,
                    "done",
                    status="error",
                    duration_ms=0,
                    stderr=reason,
                    artifact="",
                    artifact_id="",
                    wasm_sha256="",
                    attack_type=attack_type,
                )

                continue

            await _send(
                websocket,
                "compiled",
                artifact_id=compiled.artifact_id,
                wasm_sha256=compiled.wasm_sha256,
                compiler_log=compiled.compiler_log,
                attack_type=attack_type,
            )

            record_execution()

            result = run_extism_artifact(compiled.wasm_path)

            if result.stdout:
                await _send(
                    websocket,
                    "stdout",
                    chunk=result.stdout,
                )

            record_execution_result(
                status=result.status,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=result.duration_ms,
                artifact_id=compiled.artifact_id,
                wasm_sha256=compiled.wasm_sha256,
                attack_type=attack_type,
            )

            await _send(
                websocket,
                "done",
                status=result.status,
                duration_ms=result.duration_ms,
                stderr=result.stderr,
                artifact=result.artifact,
                artifact_id=compiled.artifact_id,
                wasm_sha256=compiled.wasm_sha256,
                attack_type=attack_type,
            )

    except WebSocketDisconnect:
        pass