# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# HP.1910.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "HP.1910.get_chassis_id"
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## HP.1910.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "HP.1910.get_chassis_id"
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_mac = re.compile(r"^MAC_ADDRESS\s+:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                macs = []
                for v in self.snmp.get_tables(["1.3.6.1.2.1.2.2.1.6"]):
                    if v[1] != '\x00\x00\x00\x00\x00\x00':
                        macs += [v[1]]
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                macs = []
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.2.2.1.6"], bulk=True):
                        macs += [v[1]]
                macs.remove('\x00\x00\x00\x00\x00\x00')
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
                return mac
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
<<<<<<< HEAD
        v = self.cli("display device manuinfo", cached=True)
        match = self.rx_mac.search(v)
=======
        match = self.rx_mac.search(self.cli("display device manuinfo", cached=True))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
<<<<<<< HEAD
        }
=======
            }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
