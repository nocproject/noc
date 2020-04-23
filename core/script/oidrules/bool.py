# ----------------------------------------------------------------------
# BooleanRule
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from .oid import OIDRule


class BooleanRule(OIDRule):
    """
    SNMP OID for booleans
    """

    name = "bool"
    default_type = "bool"
