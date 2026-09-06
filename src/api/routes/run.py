from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException

from src.metrics.prometheus import record_compile_error, record_execution
from src.sandbox.ast_guard import lint_source
from src.sandbox.attack_classifier import classify_source
from src.sandbox.compiler_client import CompilerError, compile_python
from src.sandbox.extism_runtime import run_extism_artifact
from src.sandbox.runtime import resolve_compiled_artifact, run_wasm
from src.storage.repository import record_execution_result

router = APIRouter(prefix="/api", tags=["run"])


class RunRequest(BaseModel):
    source: str = ""
    artifact_id: str = Field(
        default="",
        description="Compiled artifact id from POST /api/compile (loads from artifacts/)",
    )


class WasmRunRequest(BaseModel):
    artifact: str = Field(
        default="hello",
        description=(
            "WASM filename or stem under plugins/examples "
            "(e.g. hello or hello.wasm)"
        ),
    )
    stdin: str = ""


class ExecutionResult(BaseModel):
    status: str = "error"
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    message: str = ""
    artifact: str = ""
    artifact_id: str = ""
    wasm_sha256: str = ""
    attack_type: str = "none"


@router.post("/run/wasm", response_model=ExecutionResult)
def run_wasm_artifact(body: WasmRunRequest) -> ExecutionResult:
    """Run an existing WASM example."""

    record_execution()

    try:
        result = run_wasm(
            body.artifact,
            stdin=body.stdin,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    record_execution_result(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact_id="",
        wasm_sha256="",
        attack_type="none",
    )

    return ExecutionResult(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact=result.artifact,
        message="WASM execution complete",
        attack_type="none",
    )


@router.post("/run", response_model=ExecutionResult)
def run_plugin(body: RunRequest) -> ExecutionResult:
    """Compile and run source code, or run an existing compiled artifact."""

    # Existing compiled artifact execution does not contain new source code
    # to classify, so the security classification defaults to "none".
    if body.artifact_id:
        record_execution()

        try:
            wasm_path = resolve_compiled_artifact(body.artifact_id)
        except FileNotFoundError as exc:
            raise HTTPException(
                status_code=404,
                detail=str(exc),
            ) from exc
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        result = run_extism_artifact(wasm_path)

        record_execution_result(
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            artifact_id=body.artifact_id,
            wasm_sha256="",
            attack_type="none",
        )

        return ExecutionResult(
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            artifact=result.artifact,
            artifact_id=body.artifact_id,
            message="Extism plugin execution complete",
            attack_type="none",
        )

    if not body.source.strip():
        record_execution_result(
            status="error",
            stderr="Provide source code or artifact_id",
            attack_type="none",
        )

        return ExecutionResult(
            status="error",
            stderr="Provide source code or artifact_id",
            message="Provide source code or artifact_id",
            attack_type="none",
        )

    # Classify the submitted source before linting and compilation.
    # The classifier must return a string such as:
    # "safe", "filesystem", "network", "process", "environment",
    # "dynamic_import", "dangerous_builtin", "multiple", or "none".
    attack_type = classify_source(body.source)

    violations = lint_source(body.source)

    if violations:
        reason = violations[0].message

        record_execution_result(
            status="blocked",
            stderr=reason,
            attack_type=attack_type,
        )

        return ExecutionResult(
            status="blocked",
            stderr=reason,
            message="AST guard rejected source before compile",
            attack_type=attack_type,
        )

    try:
        compiled = compile_python(body.source)
    except CompilerError as exc:
        record_compile_error()
        reason = exc.log or str(exc)

        record_execution_result(
            status="error",
            stderr=reason,
            attack_type=attack_type,
        )

        return ExecutionResult(
            status="error",
            stderr=reason,
            message=str(exc),
            attack_type=attack_type,
        )

    record_execution()

    result = run_extism_artifact(compiled.wasm_path)

    record_execution_result(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact_id=compiled.artifact_id,
        wasm_sha256=compiled.wasm_sha256,
        attack_type=attack_type,
    )

    return ExecutionResult(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact=result.artifact,
        artifact_id=compiled.artifact_id,
        wasm_sha256=compiled.wasm_sha256,
        message="Compile and run complete",
        attack_type=attack_type,
    )