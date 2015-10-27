# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Supertel.K2X.get_chassis_id"
    implements = [IGetChassisID]
    cache = True

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                macs = []
                for v in self.snmp.get_tables(["1.3.6.1.2.1.2.2.1.6"],
                                              bulk=True):
                    macs += [v[1]]
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_mac.search(self.cli("show system", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
