"""Run Extism-compiled WASM plugins via the host SDK — Week 2 Day 8."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from extism import Plugin

from src.sandbox.runtime import WasmRunResult

# Maximum wall-clock seconds an Extism plugin may run before the thread is
# abandoned and an error result is returned.  Extism has no native fuel/epoch
# API, so we use a daemon thread + join-with-timeout approach.
_EXTISM_TIMEOUT_SECONDS = 5.0


def run_extism_artifact(
    wasm_path: Path,
    *,
    function: str = "greet",
) -> WasmRunResult:
    """Execute a compiled Extism plugin artifact and return stdout-style output.

    The *function* parameter is the exported PDK function name to call.
    Extism plugins compiled from the default template export ``greet``; custom
    plugins may export any name — callers should pass the correct name.

    A 5-second wall-clock timeout is enforced via a daemon thread so that a
    hung plugin cannot block the API server indefinitely.
    """
    started = time.perf_counter()

    # Mutable container shared between threads
    _result: dict = {"status": "ok", "stdout": "", "stderr": ""}

    def _run() -> None:
        try:
            plugin = Plugin(str(wasm_path), wasi=True)
            if not plugin.function_exists(function):
                _result["status"] = "error"
                _result["stderr"] = f"Plugin does not export function '{function}'"
                return

            output = plugin.call(function, b"")
            if isinstance(output, bytes):
                _result["stdout"] = output.decode("utf-8", errors="replace")
            else:
                _result["stdout"] = str(output)
        except Exception as exc:  # noqa: BLE001
            _result["status"] = "error"
            _result["stderr"] = str(exc)

    worker = threading.Thread(target=_run, daemon=True)
    worker.start()
    worker.join(timeout=_EXTISM_TIMEOUT_SECONDS)

    if worker.is_alive():
        # Thread is still blocked — plugin timed out
        duration_ms = int((time.perf_counter() - started) * 1000)
        return WasmRunResult(
            status="timeout",
            stdout="",
            stderr=f"Extism plugin exceeded {_EXTISM_TIMEOUT_SECONDS}s wall-clock limit",
            duration_ms=duration_ms,
            artifact=wasm_path.name,
        )

    duration_ms = int((time.perf_counter() - started) * 1000)
    return WasmRunResult(
        status=_result["status"],
        stdout=_result["stdout"],
        stderr=_result["stderr"],
        duration_ms=duration_ms,
        artifact=wasm_path.name,
    )
