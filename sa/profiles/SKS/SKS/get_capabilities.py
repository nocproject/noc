# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "SKS.SKS.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        try:
            cmd = self.cli("show lldp configuration")
            return "LLDP state: Enabled" in cmd
        except self.CLISyntaxError:
            # On SKS-16E1-IP-I-4P Series Software, Version 2.2.0C Build 40897
            # we are not have way, to see, if lldp enabled global
            return True

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        try:
            cmd = self.cli("show spanning-tree active")
            return "  enabled  " in cmd
        except self.CLISyntaxError:
            cmd = self.cli("show spanning-tree")
            return "No spanning tree instance exists" not in cmd
