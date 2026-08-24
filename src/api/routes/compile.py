from pydantic import BaseModel

from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["compile"])


class CompileRequest(BaseModel):
    source: str = ""


class CompileResult(BaseModel):
    status: str = "stub"
    artifact_id: str = ""
    wasm_sha256: str = ""
    message: str = "Stub response — implement Week 2 Day 7"


@router.post("/compile", response_model=CompileResult)
def compile_plugin(body: CompileRequest) -> CompileResult:
    return CompileResult(
        status="stub",
        message=f"AST guard + Docker compile — Week 2 Day 7 ({len(body.source)} chars received)",
    )
