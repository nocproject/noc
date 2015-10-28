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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID

rx_mac = re.compile(r"^System MAC:\s+(?P<mac>\S+)$", re.MULTILINE)


class Script(BaseScript):
    name = "Extreme.XOS.get_chassis_id"
    interface = IGetChassisID
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
