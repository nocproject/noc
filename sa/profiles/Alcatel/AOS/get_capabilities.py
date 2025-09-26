# ----------------------------------------------------------------------
# Alcatel.AOS.get_capabilities
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Alcatel.AOS.get_capabilities"
    cache = True

    rx_lldp = re.compile(r"^\s*\d+/\d+\s+Rx \+ Tx\s+", re.MULTILINE)
    rx_udld = re.compile(r"Global UDLD Status\s*:\s*(?P<status>\S+)")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp config")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_udld_cli(self):
        """
        Check box has UDLD enabled
        """
        r = self.cli("show udld configuration")
        match = self.rx_udld.search(r)
        return match and match.group("status") == "enabled"

    @false_on_cli_error
    def has_stack(self):
        """
        Check stack members
        :return:
        """
        v = self.cli("show module")
        v = parse_table(v.replace("\n\n", "\n"))
        return [l[0].split("-")[1] for l in v if "NI-" in l[0]]

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check lacp ports
        @todo scripts.get_portchannel
        :return:
        """
        return self.cli("show linkagg")
        # r = self.scripts.get_portchannel()

    def execute_platform_cli(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
