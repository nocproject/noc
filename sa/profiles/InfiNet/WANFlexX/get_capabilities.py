# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_capabilities"

    rx_lldp = re.compile(r"LLDP Mode: (?P<mode>(?:TxRx|Tx only|Rx only|disabled))")

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("lldp report")
        match = self.rx_lldp.search(cmd)
        return match.group("mode") != "disabled"
