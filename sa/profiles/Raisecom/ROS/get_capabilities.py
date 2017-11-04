# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_capabilities
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
    name = "Raisecom.ROS.get_capabilities"

    rx_lldp = re.compile(r"LLDP enable status:\s+enable")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp local config")
        return self.rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show spanning-tree")
        return "Disable" not in cmd
