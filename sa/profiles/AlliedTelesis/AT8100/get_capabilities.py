# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "AlliedTelesis.AT8100.get_capabilities"
    cache = True

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp")
        return ".. Enabled" in cmd

    @false_on_cli_error
    def has_stp_cli(self):
        """
        Check box has STP enabled
        """
        cmd = self.cli("show switch", cached=True)
        return "RSTP" in cmd
