# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "SKS.SKS.get_capabilities"

    rx_stack = re.compile(
        r"^\s+(?P<box_id>\d+)\s+\d+\S+\s+\d+\S+\s+ \d+\S+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        try:
            cmd = self.cli("show lldp configuration")
            return "LLDP state: Enabled" in cmd
        except self.CLISyntaxError:
            # On SKS-16E1-IP-I-4P Series Software, Version 2.2.0C Build 40897
            # we are not have way, to see, if lldp enabled global
            return True

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        try:
            cmd = self.cli("show spanning-tree active")
            return "  enabled  " in cmd
        except self.CLISyntaxError:
            cmd = self.cli("show spanning-tree")
            return "No spanning tree instance exists" not in cmd

    def execute_platform_cli(self, caps):
        try:
            cmd = self.cli("show version", cached=True)
            s = []
            for match in self.rx_stack.finditer(cmd):
                s += [match.group("box_id")]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except self.CLISyntaxError:
            pass
