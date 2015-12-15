# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_capabilities_ex
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetcapabilitiesex import IGetCapabilitiesEx


class Script(BaseScript):
    name = "Vyatta.Vyatta.get_capabilities_ex"
    cache = True
    interface = IGetCapabilitiesEx

    def execute(self, caps=None):
        caps = caps or {}
        self.check_lldp(caps)
        return caps

    def check_lldp(self, caps):
        """
        Check box has lldp enabled
        """
        r = self.cli("show lldp neighbors")
        if "LLDP not configured" not in r:
            caps["Network | LLDP"] = True
