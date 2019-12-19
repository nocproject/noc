# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.NetXpert.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Nateks.NetXpert.get_capabilities"

    rx_lacp_id = re.compile(r"^\s+(?P<id>\d+)\s+\d+", re.MULTILINE)

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("sh configuration", cached=True)
        return "spanning-tree" in cmd

    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show configuration\r\n")
        return "lldp run" in cmd
