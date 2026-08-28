from fastapi.testclient import TestClient

from src.api.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "wasmbox"


def test_lint_rejects_malicious_code():
    client = TestClient(app)

    response = client.post(
        "/api/lint",
        json={"source": 'open("/etc/passwd").read()'},
    )

    assert response.status_code == 200

    body = response.json()

    assert "violations" in body
    assert len(body["violations"]) > 0

    violation = body["violations"][0]

    assert "line" in violation
    assert "col" in violation
    assert "message" in violation
    assert "rule" in violation

    assert violation["rule"] == "blocked-call"