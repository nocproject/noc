# ---------------------------------------------------------------------
# Rotek.BT.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Rotek.BT.get_capabilities"
    cache = True

    def execute_platform_snmp(self, caps):
        if self.match_version(platform__regex="BT.*"):
            caps["Sensor | Controller"] = True
