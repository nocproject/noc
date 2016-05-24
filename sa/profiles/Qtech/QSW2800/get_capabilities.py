# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Qtech.QSW2800.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        cmd = self.cli("show lldp")
        return "LLDP has been enabled globally" in cmd

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        # Spanning Tree Enabled/Disabled : Enabled
        cmd = self.cli("show spanning-tree")
        return "Global MSTP is disabled" not in cmd