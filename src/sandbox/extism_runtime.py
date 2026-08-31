"""Run Extism-compiled WASM plugins via the host SDK — Week 2 Day 8."""

from __future__ import annotations

import time
from pathlib import Path

from extism import Plugin

from src.sandbox.runtime import WasmRunResult


def run_extism_artifact(wasm_path: Path, *, function: str = "greet") -> WasmRunResult:
    """Execute a compiled Extism plugin artifact and return stdout-style output."""
    started = time.perf_counter()
    status = "ok"
    stdout = ""
    stderr = ""

    try:
        plugin = Plugin(str(wasm_path), wasi=True)
        if not plugin.function_exists(function):
            raise RuntimeError(f"Plugin does not export function '{function}'")

        output = plugin.call(function, b"")
        if isinstance(output, bytes):
            stdout = output.decode("utf-8", errors="replace")
        else:
            stdout = str(output)
    except Exception as exc:  # noqa: BLE001 — surface sandbox failures to API layer
        status = "error"
        stderr = str(exc)

    duration_ms = int((time.perf_counter() - started) * 1000)
    return WasmRunResult(
        status=status,
        stdout=stdout,
        stderr=stderr,
        duration_ms=duration_ms,
        artifact=wasm_path.name,
    )
