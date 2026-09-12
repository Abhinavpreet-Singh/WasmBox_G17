"""Capability enum + CapabilitySet tests."""

from src.sandbox.capabilities import Capability, CapabilitySet


def test_none_grants_nothing():
    capabilities = CapabilitySet.none()
    assert not capabilities.has(Capability.ALLOW_DB_BRIDGE)
    assert not capabilities.has(Capability.ALLOW_HTTP_FETCH)


def test_from_flags_grants_only_requested_capability():
    capabilities = CapabilitySet.from_flags(allow_db_bridge=True)
    assert capabilities.has(Capability.ALLOW_DB_BRIDGE)
    assert not capabilities.has(Capability.ALLOW_HTTP_FETCH)


def test_from_flags_can_grant_both():
    capabilities = CapabilitySet.from_flags(allow_db_bridge=True, allow_http_fetch=True)
    assert capabilities.has(Capability.ALLOW_DB_BRIDGE)
    assert capabilities.has(Capability.ALLOW_HTTP_FETCH)


def test_capability_set_is_frozen():
    capabilities = CapabilitySet.none()
    try:
        capabilities.granted = frozenset({Capability.ALLOW_DB_BRIDGE})
        assert False, "CapabilitySet should be immutable"
    except AttributeError:
        pass