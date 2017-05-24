# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES.get_capabilities
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
    name = "Eltex.MES.get_capabilities"

    rx_lldp_en = re.compile(r"LLDP state: Enabled?")
    rx_gvrp_en = re.compile(r"GVRP Feature is currently Enabled on the device?")
    rx_stp_en = re.compile(r"Spanning tree enabled mode?")


    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled on Eltex
        """
        cmd = self.cli("show lldp configuration", ignore_errors = True)
        return self.rx_lldp_en.search(cmd) is not None

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has stp enabled on Eltex
        """
        cmd = self.cli("show spanning-tree", ignore_errors = True)
        return self.rx_stp_en.search(cmd) is not None

    @false_on_cli_error
    def has_gvrp(self):
        """
        Check box has gvrp enabled on Eltex
        """
        cmd = self.cli("show gvrp configuration", ignore_errors = True)
        return self.rx_gvrp_en.search(cmd) is not None
        # Get GVRP interfaces
