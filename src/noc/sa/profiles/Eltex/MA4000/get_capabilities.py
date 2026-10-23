# ---------------------------------------------------------------------
# Eltex.MA4000.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Eltex.MA4000.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp configuration")
        return "LLDP state: Enabled" in cmd

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree active")
        return "spanning tree: off" not in cmd

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has STP enabled
        """
        return any(ch["type"] == "L" for ch in self.scripts.get_portchannel())
