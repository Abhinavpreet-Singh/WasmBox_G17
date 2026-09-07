"""Sandbox security tests — Week 3 Day 11."""

from src.sandbox.ast_guard import lint_source


def test_file_read_is_blocked():
    source = 'open("/etc/passwd").read()'

    violations = lint_source(source)

    assert violations
    assert any(v.rule == "blocked-call" for v in violations)


def test_socket_import_is_blocked():
    source = "import socket"

    violations = lint_source(source)

    assert violations
    assert any(v.rule == "blocked-import" for v in violations)


def test_subprocess_import_is_blocked():
    source = "import subprocess"

    violations = lint_source(source)

    assert violations
    assert any(v.rule == "blocked-import" for v in violations)