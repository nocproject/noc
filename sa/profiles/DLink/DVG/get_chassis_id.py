# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# DLink.DVG.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "DLink.DVG.get_chassis_id"
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## DLink.DVG.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "DLink.DVG.get_chassis_id"
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_mac = re.compile(r"^WAN MAC \[+(?P<mac>\S+)+\]$", re.MULTILINE)

    def execute(self):
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
            try:
                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.2",
                                    cached=True)  # IF-MIB
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }
=======
        if self.snmp and self.access_profile.snmp_ro:
            try:
                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.2",
                                    cached=True)  # IF-MIB
                return mac
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.re_search(self.rx_mac,
                               self.cli("GET STATUS WAN", cached=True))
        if not match:
            raise self.NotSupportedError()
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
