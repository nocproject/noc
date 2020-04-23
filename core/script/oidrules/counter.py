# ----------------------------------------------------------------------
# CounterRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class CounterRule(OIDRule):
    """
    SNMP OID for SNMP counters
    """

    name = "counter"
    default_type = "counter"
