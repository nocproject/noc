# ----------------------------------------------------------------------
# Input Data Sources
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum
from typing import FrozenSet

CODE_SOURCE_MAP = {
    "e": "etl",
    "d": "discovery",
    "m": "manual"
}

SOURCE_PRIORITY = "meo"


class InputSource(enum.Enum):
    """
    Source for setting data item
    """

    ETL = "etl"
    DISCOVERY = "discovery"
    MANUAL = "manual"

    @classmethod
    def from_sources(cls, code) -> FrozenSet["InputSource"]:
        return frozenset(InputSource(CODE_SOURCE_MAP[c]) for c in code)
