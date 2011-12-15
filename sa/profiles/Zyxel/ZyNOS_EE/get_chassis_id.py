# -*- coding: utf-8 -*-
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
    cache = True

    rx_ver = re.compile(
        r"^\sMAC Address\s:\s+(?P<id>\S+).",
        re.IGNORECASE | re.MULTILINE | re.DOTALL)

    def execute(self):
        # Try SNMP first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                mac = self.snmp.get("1.3.6.1.2.1.17.1.1.0", cached=True)
                return mac
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        match = self.rx_ver.search(self.cli("sys mrd atsh", cached=True))
        return match.group("id")
