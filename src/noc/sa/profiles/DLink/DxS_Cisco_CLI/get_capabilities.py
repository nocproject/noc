# ---------------------------------------------------------------------
# DLink.DxS_Cisco_CLI.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_capabilities"

    rx_lldp = re.compile(r"Global status of LLDP\s+: Enable$", re.MULTILINE)
    rx_cdp = re.compile(
        r"Global status of LLDP\s+: Enable\nGlobal cdp compliance\s+: YES", re.MULTILINE
    )

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp status | include Global")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        cmd = self.cli("show lldp status | include Global")
        return self.rx_cdp.search(cmd) is not None

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has stp enabled
        """
        cmd = self.cli("show spanning-tree summary")
        return "No spanning tree instance exists." not in cmd
