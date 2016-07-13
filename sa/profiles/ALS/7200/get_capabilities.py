# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## ALS.7200.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript
from noc.sa.profiles.Generic.get_capabilities import false_on_cli_error
from noc.lib.mib import mib


class Script(BaseScript):
    name = "ALS.7200.get_capabilities"

    @false_on_cli_error
    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp")
        return "LLDP transmit/receive disabled on all interfaces." not in r
