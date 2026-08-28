from pydantic import BaseModel

from fastapi import APIRouter

from src.sandbox.ast_guard import lint_source

router = APIRouter(prefix="/api", tags=["lint"])


class LintRequest(BaseModel):
    source: str = ""


class LintViolation(BaseModel):
    line: int
    col: int
    message: str
    rule: str


class LintResult(BaseModel):
    violations: list[LintViolation]


@router.post("/lint", response_model=LintResult)
def lint_plugin(body: LintRequest) -> LintResult:
    violations = lint_source(body.source)

    return LintResult(
        violations=[
            LintViolation(
                line=violation.line,
                col=violation.col,
                message=violation.message,
                rule=violation.rule,
            )
            for violation in violations
        ]
    )