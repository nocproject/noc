# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Linksys.SPS2xx.get_chassis_id
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
    name = "Linksys.SPS2xx.get_chassis_id"
    interface = IGetChassisID
=======
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_chassis_id
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
    name = "Linksys.SPS2xx.get_chassis_id"
    implements = [IGetChassisID]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    cache = True

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        # BUG http://bt.nocproject.org/browse/NOC-36
        # Try snmp first
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
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.re_search(self.rx_mac,
                               self.cli("show system", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
