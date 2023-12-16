# ---------------------------------------------------------------------
# HP.Aruba.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "HP.Aruba.get_capabilities"
    rx_lldp = re.compile(r"LLDP Enabled\s+:\s*Yes")
    rx_stp = re.compile(r"Spanning tree status\s+:\s*Enabled")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp configuration")
        return bool(self.rx_lldp.search(cmd))

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree")
        return bool(self.rx_stp.search(cmd))

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show lacp configuration")
        return r
