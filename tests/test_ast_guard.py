from src.sandbox.ast_guard import lint_source


def test_file_read_is_blocked():
    source = 'open("/etc/passwd").read()'

    violations = lint_source(source)

    assert any(
        violation.rule == "blocked-call"
        and violation.message == "Call to 'open' is not allowed"
        for violation in violations
    )


def test_socket_import_is_blocked():
    source = "import socket"

    violations = lint_source(source)

    assert any(
        violation.rule == "blocked-import"
        and violation.message == "Import of 'socket' is not allowed"
        for violation in violations
    )


def test_subprocess_import_is_blocked():
    source = "import subprocess"

    violations = lint_source(source)

    assert any(
        violation.rule == "blocked-import"
        and violation.message == "Import of 'subprocess' is not allowed"
        for violation in violations
    )


def test_os_import_is_blocked():
    source = "import os"

    violations = lint_source(source)

    assert any(
        violation.rule == "blocked-import"
        and violation.message == "Import of 'os' is not allowed"
        for violation in violations
    )


def test_wildcard_import_is_blocked():
    source = "from os import *"

    violations = lint_source(source)

    rules = {violation.rule for violation in violations}

    assert "blocked-import" in rules
    assert "blocked-import-star" in rules


def test_eval_is_blocked():
    source = "eval('1 + 1')"

    violations = lint_source(source)

    assert any(violation.rule == "blocked-call" for violation in violations)


def test_exec_is_blocked():
    source = "exec('print(1)')"

    violations = lint_source(source)

    assert any(violation.rule == "blocked-call" for violation in violations)