"""Prometheus metrics endpoint."""

from fastapi import APIRouter, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics() -> Response:
    """Expose Prometheus counters in text exposition format for scraping."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)