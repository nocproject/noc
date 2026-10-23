# ---------------------------------------------------------------------
# BDCOM.xPON.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "BDCOM.xPON.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        #  Check box has lldp enabled
        r = self.cli("show lldp neighbors")
        return "LLDP is not enabled" not in r

    @false_on_cli_error
    def has_stp_cli(self):
        #  Check box has stp enabled
        r = self.cli("show spanning-tree")
        return not (
            "No spanning tree instance exists." in r or "No spanning tree instances exists." in r
        )

    def execute_platform_cli(self, caps):
        caps["Network | PON | OLT"] = True

    def execute_platform_snmp(self, caps):
        caps["Network | PON | OLT"] = True
