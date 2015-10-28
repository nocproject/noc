# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID

rx_mac = re.compile(r"^MAC address\s+:\s+(?P<mac>\S+)$", re.MULTILINE)
rx_mac1 = re.compile(
    r"^\d+\s+(?P<mac>\S+)\s+STATIC\s+System\s+CPU$", re.MULTILINE)


class Script(BaseScript):
    name = "Qtech.QSW.get_chassis_id"
    interface = IGetChassisID
    cache = True


    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                mac = self.snmp.get("1.3.6.1.4.1.27514.1.2.1.1.1.1.0", cached=True)
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = rx_mac.search(self.cli("show version", cached=True))
        if not match:
            v = self.cli("show mac-address-table static")
            match = rx_mac1.search(v)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
