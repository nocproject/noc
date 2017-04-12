# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.PON.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Eltex.PON.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^\s+MAC address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        """
        if self.has_snmp():
            try:
                mac = self.snmp.get("1.3.6.1.2.1.17.1.1.0", cached=True)
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }
                return mac
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        with self.profile.switch(self):
            mac = self.cli("show interfaces mac-address front-port 0\r",
                cached=True)
            match = self.rx_mac.search(mac)
            mac1 = match.group("mac")
            mac = self.cli("show interfaces mac-address pon-port 7\r",
                cached=True)
            match = self.rx_mac.search(mac)
            mac2 = match.group("mac")
        return {
            "first_chassis_mac": mac1,
            "last_chassis_mac": mac2
        }
