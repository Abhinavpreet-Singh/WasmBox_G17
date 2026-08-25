from pydantic import BaseModel, Field

from fastapi import APIRouter, HTTPException

from src.sandbox.runtime import run_wasm

router = APIRouter(prefix="/api", tags=["run"])


class RunRequest(BaseModel):
    source: str = ""


class WasmRunRequest(BaseModel):
    artifact: str = Field(
        default="hello",
        description="WASM filename or stem under plugins/examples (e.g. hello or hello.wasm)",
    )
    stdin: str = ""


class ExecutionResult(BaseModel):
    status: str = "stub"
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    message: str = "Stub response — implement Week 2 Day 8"
    artifact: str = ""


@router.post("/run/wasm", response_model=ExecutionResult)
def run_wasm_artifact(body: WasmRunRequest) -> ExecutionResult:
    try:
        result = run_wasm(body.artifact, stdin=body.stdin)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
    preview = body.source.strip().split("\n")[0][:80] if body.source else ""
    return ExecutionResult(
        status="stub",
        stdout=f"[stub] Received {len(body.source)} chars. First line: {preview}",
        message="Connect Wasmtime runtime in Week 2 Day 8",
    )
