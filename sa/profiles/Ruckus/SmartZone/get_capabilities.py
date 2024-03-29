# ---------------------------------------------------------------------
# Ruckus.SmartZone.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Ruckus.SmartZone.get_capabilities"
    cache = True

    def execute_platform_snmp(self, caps):
        if self.is_platform_smartzone:
            caps["CPE | Controller"] = True

    def execute_platform_cli(self, caps):
        if self.is_platform_smartzone:
            caps["CPE | Controller"] = True
