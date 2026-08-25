"""Wasmtime runtime tests — Week 1 Day 2."""

from src.sandbox.runtime import run_wasm


def test_run_hello_wasm():
    result = run_wasm("hello")
    assert result.status == "ok"
    assert "Hello from WASM" in result.stdout
    assert result.duration_ms >= 0
    assert result.artifact == "hello.wasm"
