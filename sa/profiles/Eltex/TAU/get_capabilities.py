# ---------------------------------------------------------------------
# Eltex.TAU.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Eltex.TAU.get_capabilities"

    CHECK_SNMP_GET = {"SNMP | OID | fxsMonitoring": "1.3.6.1.4.1.35265.1.9.10.5.0"}
