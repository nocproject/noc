# ---------------------------------------------------------------------
# EdgeCore.ES..get_ifindexes
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_ifindexes import Script as BaseScript


class Script(BaseScript):
    name = "EdgeCore.ES.get_ifindexes"
    INTERFACE_NAME_OID = "IF-MIB::ifName"
