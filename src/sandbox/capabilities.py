"""Capability enum and enforcement."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Capability(StrEnum):
    ALLOW_DB_BRIDGE = "ALLOW_DB_BRIDGE"
    ALLOW_HTTP_FETCH = "ALLOW_HTTP_FETCH"


@dataclass(frozen=True)
class CapabilitySet:
    """The capabilities granted to a single WASM execution.

    Immutable and empty by default — an execution has to opt into every
    capability it wants; nothing is granted implicitly.
    """

    granted: frozenset[Capability] = field(default_factory=frozenset)

    def has(self, capability: Capability) -> bool:
        return capability in self.granted

    @classmethod
    def none(cls) -> "CapabilitySet":
        """No host functions registered — the default, safest execution mode."""
        return cls(granted=frozenset())

    @classmethod
    def from_flags(
        cls,
        *,
        allow_db_bridge: bool = False,
        allow_http_fetch: bool = False,
    ) -> "CapabilitySet":
        """Build a CapabilitySet from the boolean flags on an API request body."""
        granted: set[Capability] = set()
        if allow_db_bridge:
            granted.add(Capability.ALLOW_DB_BRIDGE)
        if allow_http_fetch:
            granted.add(Capability.ALLOW_HTTP_FETCH)
        return cls(granted=frozenset(granted))