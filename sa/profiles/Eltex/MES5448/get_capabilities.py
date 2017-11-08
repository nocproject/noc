# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES5448.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

from noc.lib.text import parse_table
# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Eltex.MES5448.get_capabilities"

    rx_stp_en = re.compile(r"Spanning Tree:\s+Enabled")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled on Eltex
        """
        for i in parse_table(self.cli("show lldp interface all")):
            if i[2] == "Enabled" or i[3] == "Enabled":
                return True
        return False

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has stp enabled on Eltex
        """
        cmd = self.cli("show spanning-tree active", ignore_errors=True)
        return self.rx_stp_en.search(cmd) is not None

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check lacp
        """
        r = self.cli("show lacp partner all")
        return "ACT|AGG" in r
