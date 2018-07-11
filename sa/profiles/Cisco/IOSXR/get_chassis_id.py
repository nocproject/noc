# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOSXR.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC


class Script(BaseScript):
    name = "Cisco.IOSXR.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_range = re.compile(
        r"Base MAC Address\s*:\s*(?P<mac>\S+)\s+"
        r"MAC Address block size\s*:\s*(?P<count>\d+)",
        re.DOTALL | re.IGNORECASE
    )

    def execute(self):
        macs = []
        if self.has_snmp():
            try:
                v = self.snmp.get("1.0.8802.1.1.2.1.3.2.0", cached=True)
                return {
                    "first_chassis_mac": v,
                    "last_chassis_mac": v
                }
            except self.snmp.TimeOutError:
                pass
        else:
            # Для CRS-16/S 4.3.2 команда ниже не выводит МАС коробки, после перебора всего дерева команд show/admin show, решение было найдено только через SNMP
            v = self.cli("admin show diag chassis eeprom-info")
            for f, t in [(mac, MAC(mac).shift(int(count) - 1))
                         for mac, count in self.rx_range.findall(v)]:
                if macs and MAC(f).shift(-1) == macs[-1][1]:
                    macs[-1][1] = t
                else:
                    macs += [[f, t]]
            return [
                {
                    "first_chassis_mac": f,
                    "last_chassis_mac": t
                } for f, t in macs
            ]
