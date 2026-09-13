"""host_functions.py capability-gating tests."""

from src.sandbox.capabilities import Capability, CapabilitySet
from src.sandbox.host_functions import build_host_functions, db_query, http_fetch


def test_no_capabilities_registers_nothing():
    assert build_host_functions(CapabilitySet.none()) == []


def test_none_arg_defaults_to_no_capabilities():
    assert build_host_functions(None) == []


def test_allow_db_bridge_registers_only_db_query():
    functions = build_host_functions(CapabilitySet.from_flags(allow_db_bridge=True))
    assert db_query in functions
    assert http_fetch not in functions


def test_allow_http_fetch_registers_only_http_fetch():
    functions = build_host_functions(CapabilitySet.from_flags(allow_http_fetch=True))
    assert http_fetch in functions
    assert db_query not in functions


def test_both_capabilities_registers_both():
    functions = build_host_functions(
        CapabilitySet.from_flags(allow_db_bridge=True, allow_http_fetch=True)
    )
    assert db_query in functions
    assert http_fetch in functions