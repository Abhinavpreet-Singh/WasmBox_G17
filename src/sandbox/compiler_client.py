"""HTTP/subprocess client to compiler Docker service — Week 2 Day 7."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import uuid
from dataclasses import dataclass
from pathlib import Path

ARTIFACTS_DIR = Path(__file__).resolve().parents[2] / "artifacts"
COMPILER_IMAGE = "wasmbox-compiler:local"
COMPILE_TIMEOUT_SECONDS = 120


@dataclass(frozen=True)
class CompiledArtifact:
    artifact_id: str
    wasm_path: Path
    wasm_sha256: str
    compiler_log: str


class CompilerError(Exception):
    def __init__(self, message: str, log: str = "") -> None:
        super().__init__(message)
        self.log = log


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def docker_available() -> bool:
    """Return True when the Docker CLI can reach a running daemon."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def compiler_image_available() -> bool:
    """Return True when the wasmbox compiler image is built locally."""
    if not docker_available():
        return False
    result = subprocess.run(
        ["docker", "image", "inspect", COMPILER_IMAGE],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0


def _docker_volume_path(path: Path) -> str:
    """Normalize a host path for Docker bind mounts on Windows."""
    resolved = path.resolve()
    return resolved.as_posix()


def compile_python(source: str, *, artifacts_dir: Path | None = None) -> CompiledArtifact:
    """Compile Python plugin source to WASM via the Dockerized extism-py toolchain."""
    if not docker_available():
        raise CompilerError(
            "Docker is not available. Start Docker Desktop and build wasmbox-compiler:local.",
        )
    if not compiler_image_available():
        raise CompilerError(
            "Compiler image not found. Run: docker compose build compiler",
        )

    base = (artifacts_dir or ARTIFACTS_DIR).resolve()
    base.mkdir(parents=True, exist_ok=True)

    artifact_id = uuid.uuid4().hex[:12]
    wasm_name = f"{artifact_id}.wasm"
    wasm_path = base / wasm_name

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False,
        encoding="utf-8",
    ) as handle:
        handle.write(source)
        py_path = Path(handle.name)

    try:
        docker_cmd = [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{_docker_volume_path(base)}:/artifacts",
            "-v",
            f"{_docker_volume_path(py_path.parent)}:/work:ro",
            COMPILER_IMAGE,
            f"/work/{py_path.name}",
            "-o",
            f"/artifacts/{wasm_name}",
        ]
        result = subprocess.run(
            docker_cmd,
            capture_output=True,
            text=True,
            timeout=COMPILE_TIMEOUT_SECONDS,
            check=False,
        )
        log = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
        if result.returncode != 0:
            raise CompilerError("Compiler failed", log)
        if not wasm_path.is_file():
            raise CompilerError("Compiler produced no WASM artifact", log)

        return CompiledArtifact(
            artifact_id=artifact_id,
            wasm_path=wasm_path,
            wasm_sha256=sha256_file(wasm_path),
            compiler_log=log,
        )
    except subprocess.TimeoutExpired as exc:
        raise CompilerError("Compiler timed out", str(exc)) from exc
    finally:
        py_path.unlink(missing_ok=True)
