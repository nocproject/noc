# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID

rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)


class Script(NOCScript):
    name = "Extreme.XOS.get_chassis_id"
    implements = [IGetChassisID]
    cache = True


    def execute(self):
        # Fallback to CLI
        match = rx_mac.search(self.cli("show switch", cached=True))
        if match:
            mac = match.group("mac").lower()
            return {
               "first_chassis_mac": mac,
               "last_chassis_mac": mac
            }
        else:
            return {}