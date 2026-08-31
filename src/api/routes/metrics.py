"""Prometheus metrics endpoint."""

from fastapi import APIRouter

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics() -> dict:
    # TODO(Day 2): return prometheus_client.generate_latest() as text/plain
    return {"status": "not_implemented"}
