"""WebSocket live execution stream."""

from __future__ import annotations

import json
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.metrics.prometheus import record_compile_error, record_execution
from src.sandbox.ast_guard import lint_source
from src.sandbox.compiler_client import CompilerError, compile_python
from src.sandbox.extism_runtime import run_extism_artifact
from src.sandbox.runtime import resolve_compiled_artifact, run_wasm
from src.storage.repository import record_execution_result

router = APIRouter(tags=["websocket"])


async def _send(ws: WebSocket, event: str, **payload) -> None:
    """Send a typed JSON frame over the WebSocket."""
    await ws.send_text(json.dumps({"event": event, **payload}))


@router.websocket("/ws/executions")
async def ws_executions(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for live execution streaming.

    Client sends one JSON message per execution request:
      { "type": "run",   "source": "<python source>" }
      { "type": "run",   "artifact_id": "<id>" }
      { "type": "wasm",  "artifact": "hello" }

    Server emits a stream of typed frames:
      { "event": "start",   ... }
      { "event": "stdout",  "chunk": "..." }
      { "event": "done",    "status": "ok"|"error"|"blocked"|"timeout",
                            "duration_ms": N, "stderr": "...",
                            "artifact": "...", "artifact_id": "...",
                            "wasm_sha256": "..." }
      { "event": "error",   "detail": "..." }
    """
    await websocket.accept()
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await _send(websocket, "error", detail="Invalid JSON")
                continue

            msg_type = msg.get("type", "run")

            # ── raw WASM run (hello.wasm / infinite_loop.wasm demo) ──────────
            if msg_type == "wasm":
                artifact = msg.get("artifact", "hello")
                stdin = msg.get("stdin", "")
                await _send(websocket, "start", artifact=artifact)
                try:
                    result = run_wasm(artifact, stdin=stdin)
                    if result.stdout:
                        await _send(websocket, "stdout", chunk=result.stdout)
                    record_execution_result(
                        status=result.status,
                        stdout=result.stdout,
                        stderr=result.stderr,
                        duration_ms=result.duration_ms,
                        artifact_id="",
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
                    )
                except (FileNotFoundError, ValueError) as exc:
                    await _send(websocket, "error", detail=str(exc))
                continue

            # ── Extism artifact_id run ────────────────────────────────────────
            if msg.get("artifact_id"):
                artifact_id = msg["artifact_id"]
                await _send(websocket, "start", artifact_id=artifact_id)
                try:
                    wasm_path = resolve_compiled_artifact(artifact_id)
                except (FileNotFoundError, ValueError) as exc:
                    await _send(websocket, "error", detail=str(exc))
                    continue

                record_execution()
                result = run_extism_artifact(wasm_path)
                if result.stdout:
                    await _send(websocket, "stdout", chunk=result.stdout)
                record_execution_result(
                    status=result.status,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    duration_ms=result.duration_ms,
                    artifact_id=artifact_id,
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
                )
                continue

            # ── compile + run from source ─────────────────────────────────────
            source = msg.get("source", "").strip()
            if not source:
                await _send(websocket, "error", detail="Provide source or artifact_id")
                continue

            # AST guard
            violations = lint_source(source)
            if violations:
                await _send(
                    websocket,
                    "done",
                    status="blocked",
                    duration_ms=0,
                    stderr=violations[0].message,
                    artifact="",
                    artifact_id="",
                    wasm_sha256="",
                    violations=[
                        {"line": v.line, "col": v.col, "rule": v.rule, "message": v.message}
                        for v in violations
                    ],
                )
                record_execution_result(
                    status="blocked",
                    stdout="",
                    stderr=violations[0].message,
                    duration_ms=0,
                    artifact_id="",
                )
                continue

            await _send(websocket, "start", phase="compile")

            try:
                compiled = compile_python(source)
            except CompilerError as exc:
                record_compile_error()
                record_execution_result(
                    status="error",
                    stdout="",
                    stderr=exc.log or str(exc),
                    duration_ms=0,
                    artifact_id="",
                )
                await _send(
                    websocket,
                    "done",
                    status="error",
                    duration_ms=0,
                    stderr=exc.log or str(exc),
                    artifact="",
                    artifact_id="",
                    wasm_sha256="",
                )
                continue

            await _send(
                websocket,
                "compiled",
                artifact_id=compiled.artifact_id,
                wasm_sha256=compiled.wasm_sha256,
                compiler_log=compiled.compiler_log,
            )

            record_execution()
            result = run_extism_artifact(compiled.wasm_path)
            if result.stdout:
                await _send(websocket, "stdout", chunk=result.stdout)
            record_execution_result(
                status=result.status,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_ms=result.duration_ms,
                artifact_id=compiled.artifact_id,
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
            )

    except WebSocketDisconnect:
        pass

