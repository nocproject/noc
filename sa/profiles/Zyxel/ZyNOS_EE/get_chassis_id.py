# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Zyxel.ZyNOS_EE.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Zyxel.ZyNOS_EE.get_chassis_id"
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_chassis_id
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
    name = "Zyxel.ZyNOS_EE.get_chassis_id"
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_ver = re.compile(
        r"^\sMAC Address\s:\s+(?P<id>\S+).",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        # Try SNMP first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                mac = self.snmp.get("1.3.6.1.2.1.17.1.1.0", cached=True)
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }
                return mac
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_ver.search(self.cli("sys mrd atsh", cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
