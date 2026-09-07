"""Capability enum and enforcement."""

from enum import StrEnum


class Capability(StrEnum):
    ALLOW_DB_BRIDGE = "ALLOW_DB_BRIDGE"