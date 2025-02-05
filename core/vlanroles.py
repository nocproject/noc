# ----------------------------------------------------------------------
# VLAN Roles
# ----------------------------------------------------------------------
# Copyright (C) 2007-2024 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import enum


class VLANRole(enum.Enum):
    PROFILE = "profile"
    DEFAULT = "default"
    STUB = "stub"
    MULTICAST = "multicast"
    VOICE = "voice"
    GUEST = "guest"
    IN_MANAGEMENT = "in-management"
    OUT_MANAGEMENT = "out-management"
    TRANSIT = "transit"
    CUSTOMER = "customer"
    ROUTING = "routing"
    MIX = "mix"
