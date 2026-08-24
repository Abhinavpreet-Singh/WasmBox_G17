import httpx


def test_health():
    """Smoke test — run API locally on :8001 before pytest."""
    try:
        r = httpx.get("http://localhost:8001/health", timeout=2.0)
    except httpx.ConnectError:
        import pytest

        pytest.skip("API not running on :8001")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["service"] == "wasmbox"
