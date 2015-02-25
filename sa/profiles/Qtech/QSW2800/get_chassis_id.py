# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_chassis_id
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
    name = "Qtech.QSW2800.get_chassis_id"
    implements = [IGetChassisID]
    cache = True

    rx_mac = re.compile(r"^\s*\S+\s+MAC\s+(?P<mac>\S+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_mac_old = re.compile(r"^\d+\s+(?P<mac>\S+)\s+\S+\s+\S+\s+CPU$")

    def execute(self):
        if self.match_version(version__gte="6.3.100.12"):
            macs = []
            cmd = self.cli("show version")
            for match in self.rx_mac.finditer(cmd):
                macs += [match.group("mac")]
            macs.sort()
            return {
                "first_chassis_mac": macs[0],
                "last_chassis_mac": macs[-1]
            }
        else:
            cmd = self.cli("show mac-address-table static | i CPU")
            match = self.rx_mac_old.match(cmd)
            if match:
                mac = match.group("mac")
            return {
                "first_chassis_mac": mac,
                "last_chassis_mac": mac
            }
