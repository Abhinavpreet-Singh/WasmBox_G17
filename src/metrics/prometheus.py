"""Prometheus metric definitions — Week 1 Day 3+."""

from prometheus_client import Counter

SANDBOX_TIMEOUTS = Counter(
    "wasmbox_sandbox_timeouts_total",
    "WASM executions stopped by fuel or epoch limits",
)

OOM_TOTAL = Counter(
    "wasmbox_oom_total",
    "WASM executions stopped by memory limits",
)


def record_sandbox_timeout() -> None:
    """Increment the counter when a WASM execution times out."""
    SANDBOX_TIMEOUTS.inc()


def record_sandbox_oom() -> None:
    """Increment the counter when a WASM execution hits the memory limit."""
    OOM_TOTAL.inc()