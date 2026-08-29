"""Compile pipeline tests — Week 2 Day 6/7."""

from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.sandbox.compiler_client import CompiledArtifact, CompilerError
from src.sandbox.ast_guard import lint_source

BENIGN_SOURCE = """from extism import plugin_fn

@plugin_fn
def greet():
    return "Hello from WasmBox!"
"""


def test_compile_blocks_malicious_source():
    client = TestClient(app)

    response = client.post(
        "/api/compile",
        json={"source": 'open("/etc/passwd").read()'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"
    assert len(body["violations"]) > 0
    assert body["violations"][0]["rule"] == "blocked-call"


def test_lint_source_blocks_before_compile():
    violations = lint_source('import socket\nsocket.create_connection(("example.com", 80))')
    assert any(violation.rule == "blocked-import" for violation in violations)


@patch("src.api.routes.compile.compile_python")
def test_compile_returns_artifact_metadata(mock_compile):
    mock_compile.return_value = CompiledArtifact(
        artifact_id="abc123",
        wasm_path=None,  # type: ignore[arg-type]
        wasm_sha256="deadbeef",
        compiler_log="compiled ok",
    )

    client = TestClient(app)
    response = client.post("/api/compile", json={"source": BENIGN_SOURCE})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["artifact_id"] == "abc123"
    assert body["wasm_sha256"] == "deadbeef"
    assert body["compiler_log"] == "compiled ok"


@patch("src.api.routes.compile.compile_python")
def test_compile_surfaces_compiler_errors(mock_compile):
    mock_compile.side_effect = CompilerError("Compiler failed", "extism error details")

    client = TestClient(app)
    response = client.post("/api/compile", json={"source": BENIGN_SOURCE})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"
    assert body["compiler_log"] == "extism error details"
