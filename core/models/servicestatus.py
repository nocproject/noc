# ----------------------------------------------------------------------
# Service Oper Status
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum


class Status(enum.IntEnum):
    UNKNOWN = 0
    UP = 1
    SLIGHTLY_DEGRADED = 2
    DEGRADED = 3
    DOWN = 4
