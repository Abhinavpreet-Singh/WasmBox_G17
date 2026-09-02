from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException

from src.metrics.prometheus import record_compile_error, record_execution
from src.sandbox.ast_guard import lint_source
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
        description="WASM filename or stem under plugins/examples (e.g. hello or hello.wasm)",
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


@router.post("/run/wasm", response_model=ExecutionResult)
def run_wasm_artifact(body: WasmRunRequest) -> ExecutionResult:
    record_execution()

    try:
        result = run_wasm(body.artifact, stdin=body.stdin)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    record_execution_result(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact_id="",
    )

    return ExecutionResult(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact=result.artifact,
        message="WASM execution complete",
    )


@router.post("/run", response_model=ExecutionResult)
def run_plugin(body: RunRequest) -> ExecutionResult:
    if body.artifact_id:
        record_execution()

        try:
            wasm_path = resolve_compiled_artifact(body.artifact_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        result = run_extism_artifact(wasm_path)

        record_execution_result(
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            artifact_id=body.artifact_id,
        )

        return ExecutionResult(
            status=result.status,
            stdout=result.stdout,
            stderr=result.stderr,
            duration_ms=result.duration_ms,
            artifact=result.artifact,
            artifact_id=body.artifact_id,
            message="Extism plugin execution complete",
        )

    if not body.source.strip():
        return ExecutionResult(
            status="error",
            message="Provide source code or artifact_id",
        )

    violations = lint_source(body.source)
    if violations:
        return ExecutionResult(
            status="blocked",
            stderr=violations[0].message,
            message="AST guard rejected source before compile",
        )

    try:
        compiled = compile_python(body.source)
    except CompilerError as exc:
        record_compile_error()

        return ExecutionResult(
            status="error",
            stderr=exc.log or str(exc),
            message=str(exc),
        )

    record_execution()

    result = run_extism_artifact(compiled.wasm_path)

    record_execution_result(
        status=result.status,
        stdout=result.stdout,
        stderr=result.stderr,
        duration_ms=result.duration_ms,
        artifact_id=compiled.artifact_id,
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
    )