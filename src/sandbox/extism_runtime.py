"""Run Extism-compiled WASM plugins via the host SDK — Week 2 Day 8."""

from __future__ import annotations

import threading
import time
from pathlib import Path

from extism import Plugin

from src.sandbox.capabilities import CapabilitySet
from src.sandbox.host_functions import build_host_functions
from src.sandbox.runtime import WasmRunResult


# Maximum wall-clock seconds an Extism plugin may run before the thread is
# abandoned and an error result is returned.
#
# Extism does not provide a native fuel/epoch API here, so a daemon thread
# with a join timeout is used to prevent a hung plugin from blocking the
# API server indefinitely.
_EXTISM_TIMEOUT_SECONDS = 5.0


def run_extism_artifact(
    wasm_path: Path,
    *,
    function: str = "greet",
    capabilities: CapabilitySet | None = None,
) -> WasmRunResult:
    """Execute a compiled Extism plugin artifact.

    Args:
        wasm_path: Path to the compiled WASM artifact.
        function: Exported PDK function name to execute.
        capabilities: Capabilities granted to the WASM plugin.

    Returns:
        WasmRunResult containing the execution status, output,
        error information, duration, and artifact name.

    The default Extism template exports a function named ``greet``.
    Custom plugins may export a different function, which callers
    can provide through the ``function`` argument.

    A 5-second wall-clock timeout is enforced using a daemon thread.
    """

    started = time.perf_counter()

    # Shared result container used by the worker thread.
    result: dict[str, str] = {
        "status": "ok",
        "stdout": "",
        "stderr": "",
    }

    def _run() -> None:
        """Execute the Extism plugin inside the worker thread."""
        try:
            plugin = Plugin(
                str(wasm_path),
                wasi=True,
                functions=build_host_functions(capabilities),
            )

            if not plugin.function_exists(function):
                result["status"] = "error"
                result["stderr"] = (
                    f"Plugin does not export function '{function}'"
                )
                return

            output = plugin.call(function, b"")

            if isinstance(output, bytes):
                result["stdout"] = output.decode(
                    "utf-8",
                    errors="replace",
                )
            else:
                result["stdout"] = str(output)

        except Exception as exc:  # noqa: BLE001
            result["status"] = "error"
            result["stderr"] = str(exc)

    worker = threading.Thread(
        target=_run,
        daemon=True,
    )

    worker.start()
    worker.join(timeout=_EXTISM_TIMEOUT_SECONDS)

    # If the worker is still running after the timeout, return a timeout
    # result. Because the thread is a daemon thread, it will not prevent
    # the application from shutting down.
    if worker.is_alive():
        duration_ms = int(
            (time.perf_counter() - started) * 1000
        )

        return WasmRunResult(
            status="timeout",
            stdout="",
            stderr=(
                "Extism plugin exceeded "
                f"{_EXTISM_TIMEOUT_SECONDS}s wall-clock limit"
            ),
            duration_ms=duration_ms,
            artifact=wasm_path.name,
        )

    duration_ms = int(
        (time.perf_counter() - started) * 1000
    )

    return WasmRunResult(
        status=result["status"],
        stdout=result["stdout"],
        stderr=result["stderr"],
        duration_ms=duration_ms,
        artifact=wasm_path.name,
    )