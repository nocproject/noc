# ----------------------------------------------------------------------
# BGP protocol constants
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# -------------------

# Python modules
import enum


class BGPState(enum.IntEnum):
    IDLE = 1
    CONNECT = 2
    ACTIVE = 3
    OPENSENT = 4
    OPENCONFIRM = 5
    ESTABSYNC = 6
    ESTABLISHED = 6
