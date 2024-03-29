# ---------------------------------------------------------------------
# DCN.DCWS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "DCN.DCWS.get_capabilities"
    cache = True

    def execute_platform_cli(self, caps):
        if self.is_platform_dcws:
            caps["CPE | Controller"] = True

    def execute_platform_snmp(self, caps):
        if self.is_platform_dcws:
            caps["CPE | Controller"] = True
