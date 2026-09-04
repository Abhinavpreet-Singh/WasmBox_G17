from src.security.classifier import (
    ATTACK_CODE_INJECTION,
    ATTACK_FILESYSTEM,
    ATTACK_NONE,
    ATTACK_NETWORK,
    ATTACK_RESOURCE_EXHAUSTION,
    ATTACK_SUBPROCESS,
    classify_source,
)


def test_file_read_is_classified_as_filesystem_access():
    assert classify_source('open("/etc/passwd").read()') == ATTACK_FILESYSTEM


def test_socket_import_is_classified_as_network_access():
    assert classify_source("import socket") == ATTACK_NETWORK


def test_subprocess_import_is_classified_as_subprocess_execution():
    assert classify_source("import subprocess") == ATTACK_SUBPROCESS


def test_eval_is_classified_as_code_injection():
    assert classify_source("eval('1 + 1')") == ATTACK_CODE_INJECTION


def test_infinite_loop_is_classified_as_resource_exhaustion():
    assert classify_source("while True:\n    pass") == ATTACK_RESOURCE_EXHAUSTION


def test_safe_source_is_classified_as_none():
    assert classify_source("print('hello')") == ATTACK_NONE
