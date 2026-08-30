"""Docker compiler integration tests — skipped when Docker/image unavailable."""

import pytest

from src.sandbox.compiler_client import (
    compile_python,
    compiler_image_available,
    docker_available,
)

HELLO_PLUGIN = """from extism import plugin_fn

@plugin_fn
def greet():
    return "Hello from WasmBox!"
"""

requires_compiler = pytest.mark.skipif(
    not (docker_available() and compiler_image_available()),
    reason="Docker and wasmbox-compiler:local image required",
)


@requires_compiler
def test_compile_hello_plugin_integration(tmp_path):
    artifact = compile_python(HELLO_PLUGIN, artifacts_dir=tmp_path)

    assert artifact.artifact_id
    assert artifact.wasm_path.is_file()
    assert len(artifact.wasm_sha256) == 64
