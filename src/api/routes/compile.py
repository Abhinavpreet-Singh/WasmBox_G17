from pydantic import BaseModel, Field

from fastapi import APIRouter

from src.metrics.prometheus import record_compile_error
from src.sandbox.ast_guard import lint_source
from src.sandbox.compiler_client import CompilerError, compile_python

router = APIRouter(prefix="/api", tags=["compile"])


class CompileRequest(BaseModel):
    source: str = ""


class CompileViolation(BaseModel):
    line: int
    col: int
    message: str
    rule: str


class CompileResult(BaseModel):
    status: str = "stub"
    artifact_id: str = ""
    wasm_sha256: str = ""
    message: str = ""
    violations: list[CompileViolation] = Field(default_factory=list)
    compiler_log: str = ""


@router.post("/compile", response_model=CompileResult)
def compile_plugin(body: CompileRequest) -> CompileResult:
    violations = lint_source(body.source)
    if violations:
        return CompileResult(
            status="blocked",
            message="AST guard rejected source before compile",
            violations=[
                CompileViolation(
                    line=violation.line,
                    col=violation.col,
                    message=violation.message,
                    rule=violation.rule,
                )
                for violation in violations
            ],
        )

    try:
        artifact = compile_python(body.source)
    except CompilerError as exc:
        record_compile_error()
        return CompileResult(
            status="error",
            message=str(exc),
            compiler_log=exc.log,
        )

    return CompileResult(
        status="ok",
        artifact_id=artifact.artifact_id,
        wasm_sha256=artifact.wasm_sha256,
        message="Compile complete",
        compiler_log=artifact.compiler_log,
    )
