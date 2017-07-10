# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_capabilities
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
    name = "HP.Comware.get_capabilities"

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        try:
            r = self.cli("display stp global | include Enabled")
            return "?STP" in r
        except self.CLISyntaxError:
            r = self.cli("display stp | include Enabled")
            return "?STP" in r

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        rx_lldp = re.compile(r"Global status of LLDP: Enable")
        cmd = self.cli("display lldp status | include Global")
        return rx_lldp.search(cmd) is not None

    @false_on_cli_error
    def has_ndp(self):
        """
        Check box has NDP enabled
        """
        r = self.cli("display ndp")
        return "enabled" in r

    def execute_platform(self, caps):
        if self.has_ndp():
            caps["Huawei | NDP"] = True
