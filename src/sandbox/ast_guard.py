"""AST-based security guard for untrusted Python source."""

import ast
from dataclasses import dataclass


BLOCKED_MODULES = {"os", "socket", "subprocess", "ctypes", "importlib", "builtins"}
BLOCKED_CALLS = {"open", "eval", "exec", "__import__", "compile", "breakpoint"}

# Attribute chains that must be blocked even without a direct import
# e.g. someone does: x = __builtins__; x['open']('/etc/passwd')
BLOCKED_ATTRIBUTES = {"system", "popen", "spawn", "fork", "execve"}


@dataclass(frozen=True)
class Violation:
    line: int
    col: int
    message: str
    rule: str


def lint_source(source: str) -> list[Violation]:
    """Return security violations found in Python source code."""
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [
            Violation(
                line=exc.lineno or 1,
                col=exc.offset or 1,
                message="Invalid Python syntax",
                rule="syntax-error",
            )
        ]

    violations: list[Violation] = []

    for node in ast.walk(tree):
        # ── import os / import subprocess ────────────────────────────────────
        if isinstance(node, ast.Import):
            for alias in node.names:
                module = alias.name.split(".", 1)[0]
                if module in BLOCKED_MODULES:
                    violations.append(
                        Violation(
                            line=node.lineno,
                            col=node.col_offset + 1,
                            message=f"Import of '{module}' is not allowed",
                            rule="blocked-import",
                        )
                    )

        # ── from os import path / from importlib import * ────────────────────
        elif isinstance(node, ast.ImportFrom):
            module = (node.module or "").split(".", 1)[0]
            if module in BLOCKED_MODULES:
                violations.append(
                    Violation(
                        line=node.lineno,
                        col=node.col_offset + 1,
                        message=f"Import of '{module}' is not allowed",
                        rule="blocked-import",
                    )
                )
            if any(alias.name == "*" for alias in node.names):
                violations.append(
                    Violation(
                        line=node.lineno,
                        col=node.col_offset + 1,
                        message="Wildcard imports are not allowed",
                        rule="blocked-import-star",
                    )
                )

        # ── open(...) / eval(...) / exec(...) / __import__(...) ──────────────
        elif isinstance(node, ast.Call):
            # Direct name call: open(), eval(), __import__()
            if isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
                violations.append(
                    Violation(
                        line=node.lineno,
                        col=node.col_offset + 1,
                        message=f"Call to '{node.func.id}' is not allowed",
                        rule="blocked-call",
                    )
                )
            # Attribute call: os.system(), subprocess.Popen(), etc.
            elif isinstance(node.func, ast.Attribute):
                if node.func.attr in BLOCKED_ATTRIBUTES:
                    violations.append(
                        Violation(
                            line=node.lineno,
                            col=node.col_offset + 1,
                            message=f"Call to '.{node.func.attr}' is not allowed",
                            rule="blocked-call",
                        )
                    )

    return violations