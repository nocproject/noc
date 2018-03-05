# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DGS3100.get_capabilities
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
    name = "DLink.DGS3100.get_capabilities"

    rx_lldp = re.compile(r"LLDP Status\s+: Enabled?")
    rx_stp = re.compile(r"STP Status\s+: Enabled?")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return bool(self.rx_lldp.search(cmd))

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """

        # DGS3100 do not show any information about neighbors
        return False

        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("show stp")
        return bool(self.rx_stp.search(cmd))
