# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Raisecom.ROS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Raisecom.ROS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(r"System\s+MacAddress\s+is\s*:\s*(?P<id>\S+)",
                       re.IGNORECASE | re.MULTILINE)

    def execute(self):
        result = []
        v = self.cli("show version")
        match = self.re_search(self.rx_id, v)
        mac = match.group("id")
        return [{
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }]
