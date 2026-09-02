"""Sandbox health and runtime configuration."""

import time

from fastapi import APIRouter

from src.sandbox.runtime import DEFAULT_MEMORY_BYTES

router = APIRouter(tags=["health"])

START_TIME = time.time()

FUEL_LIMIT = 100_000
MEMORY_CAP_BYTES = 64 * 1024 * 1024
TIMEOUT_SECONDS = 0.05


@router.get("/health")
def health() -> dict:
    """Return backend health and sandbox limits."""

    return {
        "status": "ok",
        "service": "wasmbox",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "fuel_limit": FUEL_LIMIT,
        "memory_cap_bytes": MEMORY_CAP_BYTES,
        "timeout_seconds": TIMEOUT_SECONDS,
    }