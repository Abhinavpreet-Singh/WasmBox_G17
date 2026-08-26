"""Wasmtime sandbox limit tests — Week 1 Day 3."""

from src.metrics.prometheus import SANDBOX_TIMEOUTS
from src.sandbox.runtime import run_wasm


def test_infinite_loop_times_out_quickly():
    result = run_wasm("infinite_loop")
    assert result.status == "timeout"
    assert result.duration_ms < 100


def test_infinite_loop_increments_timeout_counter():
    before = SANDBOX_TIMEOUTS._value.get()  # noqa: SLF001 — prometheus test hook
    run_wasm("infinite_loop")
    after = SANDBOX_TIMEOUTS._value.get()  # noqa: SLF001
    assert after == before + 1
