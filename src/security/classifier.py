"""Classify security threats detected in untrusted Python source."""

from __future__ import annotations

import ast

from src.sandbox.ast_guard import Violation, lint_source


ATTACK_NONE = "none"
ATTACK_UNKNOWN = "unknown"
ATTACK_FILESYSTEM = "filesystem_access"
ATTACK_NETWORK = "network_access"
ATTACK_SUBPROCESS = "subprocess_execution"
ATTACK_CODE_INJECTION = "code_injection"
ATTACK_RESOURCE_EXHAUSTION = "resource_exhaustion"


def _contains_infinite_loop(source: str) -> bool:
    """Return True when the source contains a loop with a constant True test."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False

    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            if isinstance(node.test, ast.Constant) and node.test.value is True:
                return True

    return False


def _classify_violation(violation: Violation) -> str:
    """Map one AST guard violation to an attack category."""
    message = violation.message.lower()

    if "open" in message:
        return ATTACK_FILESYSTEM

    if any(
        name in message
        for name in ("socket", "network")
    ):
        return ATTACK_NETWORK

    if any(
        name in message
        for name in ("subprocess", "system", "popen", "spawn", "fork", "execve")
    ):
        return ATTACK_SUBPROCESS

    if any(
        name in message
        for name in ("eval", "exec", "compile", "__import__")
    ):
        return ATTACK_CODE_INJECTION

    if violation.rule == "syntax-error":
        return ATTACK_UNKNOWN

    return ATTACK_UNKNOWN


def classify_source(source: str) -> str:
    """Return the most relevant security attack category for Python source."""
    if _contains_infinite_loop(source):
        return ATTACK_RESOURCE_EXHAUSTION

    violations = lint_source(source)

    if not violations:
        return ATTACK_NONE

    categories = {
        _classify_violation(violation)
        for violation in violations
    }

    priority = (
        ATTACK_CODE_INJECTION,
        ATTACK_SUBPROCESS,
        ATTACK_NETWORK,
        ATTACK_FILESYSTEM,
        ATTACK_RESOURCE_EXHAUSTION,
        ATTACK_UNKNOWN,
    )

    for category in priority:
        if category in categories:
            return category

    return ATTACK_UNKNOWN