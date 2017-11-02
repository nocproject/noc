# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# EdgeCore.ES.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "EdgeCore.ES.get_capabilities"

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        try:
            r = self.cli("show spanning-tree brief | include Enabled/Disabled")
            r = r.strip()
            return ":" in r and r.rsplit(":", 1)[-1].strip().lower() == "enabled"
        except self.CLISyntaxError:
            r = self.cli("show spanning-tree brief")
            return "Enabled/Disabled : Enabled" in r

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled
        """
        try:
            r = self.cli("show lldp config | include LLDP Enable")
        except self.CLISyntaxError:
            r = self.cli("show lldp config")
        return "Yes" in r
