# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_capabilities
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.sa.profiles.Generic.get_capabilities import Script as BaseScript


class Script(BaseScript):
    name = "Vyatta.Vyatta.get_capabilities"

    def has_lldp(self):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp neighbors")
        return "LLDP not configured" not in r
