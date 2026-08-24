from pydantic import BaseModel

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["run"])


class RunRequest(BaseModel):
    source: str = ""


class ExecutionResult(BaseModel):
    status: str = "stub"
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    message: str = "Stub response — implement Week 2 Day 8"


@router.post("/run", response_model=ExecutionResult)
def run_plugin(body: RunRequest) -> ExecutionResult:
    preview = body.source.strip().split("\n")[0][:80] if body.source else ""
    return ExecutionResult(
        status="stub",
        stdout=f"[stub] Received {len(body.source)} chars. First line: {preview}",
        message="Connect Wasmtime runtime in Week 2 Day 8",
    )
