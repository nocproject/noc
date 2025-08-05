# ----------------------------------------------------------------------
# Input Data Sources
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import FrozenSet, List

CODE_SOURCE_MAP = {
    "e": "etl",
    "d": "discovery",
    "m": "manual",
    "c": "config",
    "o": "unknown",
    "u": "unknown",
}

SOURCE_PRIORITY = "meu"


class InputSource(enum.Enum):
    """
    Source for setting data item
    """

    ETL = "etl"
    DISCOVERY = "discovery"
    DATABASE = "database"
    # ServiceDiscovery ?
    MANUAL = "manual"
    CONFIG = "config"  # profile
    #
    UNKNOWN = "unknown"

    @classmethod
    def from_sources(cls, code) -> List["InputSource"]:
        """Convert code to InputSource List"""
        return [InputSource(CODE_SOURCE_MAP[c]) for c in code]

    @classmethod
    def to_codes(cls, sources: List["InputSource"]) -> str:
        """Convert Sources to codes"""
        return "".join(s.code for s in sources)

    @property
    def code(self) -> str:
        return self.value[0]
