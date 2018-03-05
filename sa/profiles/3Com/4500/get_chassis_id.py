# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.4500.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "3Com.4500.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile( r"^\s+First mac address\s+:\s+(?P<mac>\S+)$",
	re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                macs = []
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.2.2.1.6"], bulk=True):
                        macs += [v[1]]
		macs = [x for x in macs if x != '\x00\x00\x00\x00\x00\x00']
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
                return mac
            except self.snmp.TimeOutError:
                pass

	
        # Fallback to CLI
        match = self.rx_mac.search(self.cli("display device manuinfo", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
            }
