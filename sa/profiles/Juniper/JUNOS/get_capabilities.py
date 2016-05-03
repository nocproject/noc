# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error


class Script(BaseScript):
    name = "Juniper.JUNOS.get_capabilities"

    @false_on_cli_error
    def has_stp(self):
        """
        Check box has STP enabled
        """
        r = self.cli("show spanning-tree bridge | match Enabled")
        return "?STP" in r

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp | match Enabled")
        return "Enabled" in r
