# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW2800.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Qtech.QSW2800.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s*\S+\s+MAC\s+(?P<mac>\S+)$",
        re.MULTILINE | re.IGNORECASE)
    rx_mac_old = re.compile(r"^\d+\s+(?P<mac>\S+)\s+\S+\s+\S+\s+CPU$",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        v = self.scripts.get_version()
        if v["version"].startswith("7") \
        or self.match_version(version__gte="6.3.100.12"):
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
