# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vitesse.VSC.get_capabilities
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
    name = "Vitesse.VSC.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has LLDP enabled
        """
        return True  # Always global enabled

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree")
        return " Forwarding " in cmd

    @false_on_cli_error
    def has_oam(self):
        """
        Check box has Ethernet OAM enabled
        """
        cmd = self.cli("show link-oam")
        return "  enabled  " in cmd

    @false_on_cli_error
    def has_ipv6(self):
        """
        Check box has IPv6 ND enabled
        """
        cmd = self.cli("show ipv6 neighbor")
        return bool(cmd)
