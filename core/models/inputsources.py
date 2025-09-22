# ----------------------------------------------------------------------
# Input Data Sources
# ----------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import List, Optional, Iterable

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
    TEMPLATE = "template"
    UNKNOWN = "unknown"

    @classmethod
    def from_sources(cls, code) -> List["InputSource"]:
        """Convert code to InputSource List"""
        return [InputSource(CODE_SOURCE_MAP[c]) for c in code]

    @classmethod
    def to_codes(cls, sources: Iterable["InputSource"]) -> str:
        """Convert Sources to codes"""
        return "".join(s.code for s in sources)

    @property
    def code(self) -> str:
        return self.value[0]

    def get_priority_weight(self, priority: Optional[str] = None) -> int:
        """Return source priority. More,"""
        priority = priority or SOURCE_PRIORITY
        if self.code in priority:
            return priority.index(self.code)
        return 0
