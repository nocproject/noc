# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.XOS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Extreme.XOS.get_capabilities"

    rx_lldp = re.compile(r"^\s*\d+(\:\d+)?\s+Enabled\s+Enabled", re.MULTILINE)
    rx_cdp = re.compile(r"^\s*CDP(\s\S+|)\s*[Ee]nabled ports\s+:\s+\d+", re.MULTILINE)

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_cdp_cli(self):
        """
        Check box has CDP enabled
        """
        cmd = self.cli("show cdp")
        return self.rx_cdp.search(cmd) is not None

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has LACP enable
        Check:
        LACP Up                             : Yes
        LACP Enabled                        : Yes
        :return:
        """
        cmd = self.cli("show lacp")
        cmd = [
            c
            for c in cmd.splitlines()
            if ("LACP Up" in c and "Yes" in c) or ("LACP Enabled" in c and "Yes" in c)
        ]
        return len(cmd) == 2

    @false_on_cli_error
    def has_stack(self):
        s = []
        cmd = self.cli("show stacking")
        if "stacking-support:          Disabled" in cmd:
            return s
        for i in parse_table(cmd, footer="(Indicates this node|stacking-support:)"):
            if i[1] == "-":
                continue
            s += [i[1]]
        return s

    def execute_platform_cli(self, caps):
        s = self.has_stack()
        if s:
            caps["Stack | Members"] = len(s) if len(s) != 1 else 0
            caps["Stack | Member Ids"] = " | ".join(s)
