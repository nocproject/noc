# ---------------------------------------------------------------------
# HP.ProCurve.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "HP.ProCurve.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp config")
        return "LLDP Enabled [Yes] : Yes" in r

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        r = self.cli("show spanning-tree")
        return "STP Enabled   : Yes" in r

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lacp")
        return "Yes" in r

    @false_on_cli_error
    def has_display_cli(self):
        self.cli("display interface brief", cached=True)
        return True

    def execute_platform_cli(self, caps):
        if not self.has_display_cli():
            caps["HP | ProCurve | CLI | Old"] = True
