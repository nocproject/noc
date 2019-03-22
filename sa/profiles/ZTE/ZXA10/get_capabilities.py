# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.get_capabilities
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "ZTE.ZXA10.get_capabilities"

    @false_on_cli_error
    def has_lldp_cli(self):
        """
        Check box has LLDP enabled
        """
        cmd = self.cli("show lldp config")
        return "enabledRxTx" in cmd
