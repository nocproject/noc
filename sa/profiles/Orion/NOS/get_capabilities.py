# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Orion.NOS.get_capabilities
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
    name = "Orion.NOS.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp statistic")
        return "LLDP is not enabled." not in cmd

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree")
        return "Disable" not in cmd

    @false_on_cli_error
    def has_oam(self):
        """
        Check box has Ethernet OAM enabled
        """
        cmd = self.cli("show extended-oam status")
        # Need more examples
        return False
