"""Wasmtime Store limits, fuel, timeout — Week 1 Day 2+."""

from __future__ import annotations

import os
import tempfile
import time
import threading
from dataclasses import dataclass
from pathlib import Path

from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig

from src.metrics.prometheus import record_sandbox_oom, record_sandbox_timeout

DEFAULT_EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "plugins" / "examples"
DEFAULT_FUEL = 1_000_000
DEFAULT_MEMORY_BYTES = 16 * 1024 * 1024


@dataclass(frozen=True)
class WasmRunResult:
    status: str
    stdout: str
    stderr: str
    duration_ms: int
    artifact: str


def resolve_artifact_path(artifact: str, *, base_dir: Path | None = None) -> Path:
    """Resolve a WASM artifact name under plugins/examples (no path traversal)."""
    base = (base_dir or DEFAULT_EXAMPLES_DIR).resolve()
    name = Path(artifact).name
    if not name.endswith(".wasm"):
        name = f"{name}.wasm"
    path = (base / name).resolve()
    if base not in path.parents and path != base:
        raise ValueError("artifact path escapes examples directory")
    if not path.is_file():
        raise FileNotFoundError(f"WASM artifact not found: {name}")
    return path


def _create_engine() -> Engine:
    config = Config()
    config.consume_fuel = True
    return Engine(config)


def _create_store(engine: Engine) -> Store:
    store = Store(engine)
    store.set_limits(memory_size=DEFAULT_MEMORY_BYTES)
    store.set_fuel(DEFAULT_FUEL)
    return store


def _classify_trap(error_detail: str) -> str:
    lower = error_detail.lower()
    if "fuel" in lower or "epoch" in lower:
        return "timeout"
    return "error"


def run_wasm(
    artifact: str,
    *,
    stdin: str = "",
    base_dir: Path | None = None,
) -> WasmRunResult:
    """Load a prebuilt WASM module, optionally feed stdin, return stdout/stderr + timing."""
    wasm_path = resolve_artifact_path(artifact, base_dir=base_dir)
    started = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmp:
        stdout_path = os.path.join(tmp, "stdout.log")
        stderr_path = os.path.join(tmp, "stderr.log")
        stdin_path = os.path.join(tmp, "stdin.txt")
        if stdin:
            Path(stdin_path).write_text(stdin, encoding="utf-8")

        config = WasiConfig()
        config.stdout_file = stdout_path
        config.stderr_file = stderr_path
        if stdin:
            config.stdin_file = stdin_path

        wasm_config = Config()
        wasm_config.consume_fuel = True
        wasm_config.epoch_interruption = True

        engine = Engine(wasm_config)
        linker = Linker(engine)
        store = Store(linker.engine)
        store.set_fuel(100_000)
        store.set_epoch_deadline(1)

        timer = threading.Timer(0.05, engine.increment_epoch)
        timer.start()

        store.set_wasi(config)

        module = Module.from_file(engine, str(wasm_path))
        instance = linker.instantiate(store, module)
        start = instance.exports(store).get("_start")
        if start is None:
            raise RuntimeError("WASM module does not export _start")

        status = "ok"
        error_detail = ""
        try:
            start(store)
        except Exception as exc:  # noqa: BLE001 — surface sandbox failures to API layer
            error_detail = str(exc)
            status = _classify_trap(error_detail)
            if status == "timeout":
                record_sandbox_timeout()
            elif "memory" in error_detail.lower() or "out of memory" in error_detail.lower():
                record_sandbox_oom()

        stdout_text = Path(stdout_path).read_text(encoding="utf-8")
        stderr_text = Path(stderr_path).read_text(encoding="utf-8")
        if status != "ok" and error_detail and not stderr_text:
            stderr_text = error_detail

    duration_ms = int((time.perf_counter() - started) * 1000)
    return WasmRunResult(
        status=status,
        stdout=stdout_text,
        stderr=stderr_text,
        duration_ms=duration_ms,
        artifact=wasm_path.name,
    )
