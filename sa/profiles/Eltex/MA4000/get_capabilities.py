# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MA4000.get_capabilities
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
    name = "Eltex.MA4000.get_capabilities"

    rx_stack = re.compile(r"^\s*\*?(?P<box_id>\d+)\s+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp configuration")
        return "LLDP state: Enabled" in cmd

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree active")
        return "spanning tree: off" not in cmd

    def execute_platform(self, caps):
        try:
            cmd = self.cli("show stack")
            s = []
            for match in self.rx_stack.finditer(cmd):
                s += [match.group("box_id")]
            if s:
                caps["Stack | Members"] = len(s) if len(s) != 1 else 0
                caps["Stack | Member Ids"] = " | ".join(s)
        except:
            pass
