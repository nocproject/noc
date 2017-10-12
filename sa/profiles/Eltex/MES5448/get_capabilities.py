# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.lib.text import parse_table
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES5448.get_capabilities"

    rx_stp_en = re.compile(r"Spanning Tree:\s+Enabled")

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled on Eltex
        """
        for i in parse_table(self.cli("show lldp interface all")):
            if i[2] == "Enabled" or i[3] == "Enabled":
                return True
        return False

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has stp enabled on Eltex
        """
        cmd = self.cli("show spanning-tree active", ignore_errors=True)
        return self.rx_stp_en.search(cmd) is not None

    @false_on_cli_error
    def has_lacp(self):
        """
        Check lacp
        """
        r = self.cli("show lacp partner all")
        return "ACT|AGG" in r
