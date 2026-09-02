"""Run pipeline tests — Week 2 Day 7/8."""

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.api.main import app
from src.sandbox.compiler_client import CompiledArtifact, CompilerError
from src.sandbox.runtime import WasmRunResult

BENIGN_SOURCE = """from extism import plugin_fn

@plugin_fn
def greet():
    return "Hello from WasmBox!"
"""


@patch("src.api.routes.run.run_extism_artifact")
@patch("src.api.routes.run.resolve_compiled_artifact")
def test_run_by_artifact_id(mock_resolve, mock_run_extism):
    mock_resolve.return_value = Path("artifacts/abc123.wasm")
    mock_run_extism.return_value = WasmRunResult(
        status="ok",
        stdout="Hello from WasmBox!",
        stderr="",
        duration_ms=3,
        artifact="abc123.wasm",
    )

    client = TestClient(app)
    response = client.post("/api/run", json={"artifact_id": "abc123"})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["stdout"] == "Hello from WasmBox!"
    assert body["artifact_id"] == "abc123"


@patch("src.api.routes.run.run_extism_artifact")
@patch("src.api.routes.run.compile_python")
def test_run_compiles_and_executes_source(mock_compile, mock_run_extism):
    mock_compile.return_value = CompiledArtifact(
        artifact_id="deadbeef",
        wasm_path=Path("artifacts/deadbeef.wasm"),
        wasm_sha256="abc",
        compiler_log="ok",
    )
    mock_run_extism.return_value = WasmRunResult(
        status="ok",
        stdout="Hello from WasmBox!",
        stderr="",
        duration_ms=5,
        artifact="deadbeef.wasm",
    )

    client = TestClient(app)
    response = client.post("/api/run", json={"source": BENIGN_SOURCE})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["artifact_id"] == "deadbeef"
    assert body["wasm_sha256"] == "abc"


def test_run_blocks_malicious_source():
    client = TestClient(app)
    response = client.post(
        "/api/run",
        json={"source": 'open("/etc/passwd").read()'},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "blocked"


@patch("src.api.routes.run.compile_python")
def test_run_surfaces_compile_errors(mock_compile):
    mock_compile.side_effect = CompilerError("Compiler failed", "docker missing")

    client = TestClient(app)
    response = client.post("/api/run", json={"source": BENIGN_SOURCE})

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "error"
    assert "docker missing" in body["stderr"]
