# -*- coding: utf-8 -*-
<<<<<<< HEAD
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
=======
##----------------------------------------------------------------------
## Eltex.MES.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Eltex.MES.get_chassis_id"
    implements = [IGetChassisID]
    cache = True

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                macs = []
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.2.2.1.6"], bulk=True):
                        macs += [v[1]]
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_mac.search(self.cli("show system", cached=True))
<<<<<<< HEAD
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
=======
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        }
