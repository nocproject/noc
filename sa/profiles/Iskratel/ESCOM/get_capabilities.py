# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Iskratel.ESCOM.get_capabilities"
    cache = True

    rx_stack = re.compile(r"^\s*(?P<box_id>\d+)\s+\S+\s*\n", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        if self.is_escom_l:
            cmd = self.cli("show configuration")
            return "lldp run" in cmd
        else:
            cmd = self.cli("show lldp configuration")
            return "LLDP state: Enabled" in cmd

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        if self.is_escom_l:
            cmd = self.cli("show spanning-tree")
            return "Spanning tree enabled" in cmd
        else:
            cmd = self.cli("show spanning-tree active")
            return "  enabled  " in cmd

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check stack members
        :return:
        """
        r = self.cli("show aggregator-group summary", cached=True)
        r = parse_table(r)
        return bool(r)

    def execute_platform_cli(self, caps):
        try:
            cmd = self.cli("show system id", cached=True)
            s = []
            for match in self.rx_stack.finditer(cmd):
                s += [match.group("box_id")]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except self.CLISyntaxError:
            pass
