# ---------------------------------------------------------------------
# Planet.WGSD.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Planet.WGSD.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_lacp_en = re.compile(r"\s+Partner[\S\s]+?\s+Oper Key:\s+1", re.MULTILINE)
    rx_gvrp_en = re.compile(r"GVRP Feature is currently Enabled on the device?")
    rx_stp_en = re.compile(r"Spanning tree enabled mode?")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp configuration", ignore_errors=True)
        return self.rx_lldp_en.search(cmd) is not None

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has lacp enabled
        """
        cmd = self.cli("show lacp Port-Channel", ignore_errors=True)
        return self.rx_lacp_en.search(cmd) is not None

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled
        """
        cmd = self.cli("show spanning-tree", ignore_errors=True)
        return self.rx_stp_en.search(cmd) is not None

    @false_on_cli_error
    def has_gvrp_cli(self):
        """
        Check box has gvrp enabled
        """
        cmd = self.cli("show gvrp configuration", ignore_errors=True)
        return self.rx_gvrp_en.search(cmd) is not None
        # Get GVRP interfaces

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show version", cached=True)
        return [e[0] for e in parse_table(r)]

    def execute_platform_cli(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
