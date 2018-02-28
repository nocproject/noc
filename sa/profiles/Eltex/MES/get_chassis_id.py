# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Eltex.MES.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.mac import MAC
from noc.core.mib import mib


class Script(BaseScript):
    name = "Eltex.MES.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)
    rx_mac2 = re.compile(r"^OOB MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_cli(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                macs = set()
                for v in self.snmp.getnext(mib["IF-MIB::ifPhysAddress"]):
                    macs.add(int(MAC(v[1])))
                ranges = []
                for m in sorted(macs):
                    if not ranges or m - ranges[-1][1] != 1:
                        ranges += [[m, m]]
                    else:
                        ranges[-1][1] = m
                return [{
                    "first_chassis_mac": r[0],
                    "last_chassis_mac": r[1]
                } for r in ranges]
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_mac.search(self.cli("show system", cached=True))
        if match:
            mac_begin = match.group("mac")
            mac_end = match.group("mac")
        else:
            c = self.cli("show system unit 1", cached=True)
            match = self.rx_mac.search(c)
            mac_begin = match.group("mac")
            match = self.rx_mac2.search(c)
            mac_end = match.group("mac")
        return {
            "first_chassis_mac": mac_begin,
            "last_chassis_mac": mac_end
        }
