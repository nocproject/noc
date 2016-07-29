# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.lib.mib import mib


class Script(BaseScript):
    name = "Linux.RHEL.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("ladvdc -L")
        return "ladvdc: command not found" not in r

    @false_on_cli_error
    def has_cdp(self):
        """
        Check box has cdp enabled
        """
        r = self.cli("ladvdc -L")
        return "ladvdc: command not found" not in r
