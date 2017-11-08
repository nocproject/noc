# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_capabilities
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
    name = "Huawei.MA5600T.get_capabilities"

    rx_lacp_id = re.compile("^\s+(?P<id>\d+)\s+\d+", re.MULTILINE)

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("display current-configuration section config\r\n")
        return "stp enable" in cmd

    @false_on_cli_error
    def has_lacp_cli(self):
        """
        Check box has LACP enabled
        """
        cmd = self.cli("display lacp link-aggregation summary")
        return self.rx_lacp_id.search(cmd) is not None
