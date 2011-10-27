# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Eltex.MES.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID

rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>\S+)$", re.MULTILINE)

class Script(NOCScript):
    name = "Eltex.MES.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    def execute(self):
        # Try snmp first
# BUG http://bt.nocproject.org/browse/NOC-36
#        if self.snmp and self.access_profile.snmp_ro:
#            try:
#                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.1000", cached=True)
#                return mac
#            except self.snmp.TimeOutError:
#                pass

        # Fallback to CLI
        match = self.re_search(rx_mac, self.cli("show system", cached=True))
        return match.group("mac")
