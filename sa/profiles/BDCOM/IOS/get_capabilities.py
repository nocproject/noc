# ---------------------------------------------------------------------
# BDCOM.IOS.get_capabilities.ex
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "BDCOM.IOS.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp interface")
        return "LLDP is not enabled" not in r

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        if "No spanning tree instance exists." in r or "No spanning tree instances exists." in r:
            return False
        return True
