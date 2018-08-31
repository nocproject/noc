# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Eltex.LTP.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has lldp enabled on Eltex
        """
        with self.profile.switch(self):
            cmd = self.cli("show lldp configuration", ignore_errors=True)
            return "State: Enabled" in cmd
