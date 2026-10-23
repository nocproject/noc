# ---------------------------------------------------------------------
# Sumavision.IPQAM.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Sumavision.IPQAM.get_capabilities"

    def execute_platform_snmp(self, caps):
        caps["Network | DVBC"] = True
