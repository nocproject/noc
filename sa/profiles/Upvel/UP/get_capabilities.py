# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UPVEL.UP.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "UPVEL.UP.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        return True  # Always global enabled

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show spanning-tree", cached=True)
        return " Forwarding " in cmd

    @false_on_cli_error
    def has_oam_cli(self):
        """
        Check box has Ethernet OAM enabled
        """
        cmd = self.cli("show link-oam", cached=True)
        return "  enabled  " in cmd

    @false_on_cli_error
    def has_ipv6_cli(self):
        """
        Check box has IPv6 ND enabled
        """
        cmd = self.cli("show ipv6 neighbor")
        return bool(cmd)
