# ----------------------------------------------------------------------
# Input Data Sources
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum


class InputSource(enum.Enum):
    """
    Source for setting data item
    """

    ETL = "etl"
    DISCOVERY = "discovery"
    MANUAL = "manual"
