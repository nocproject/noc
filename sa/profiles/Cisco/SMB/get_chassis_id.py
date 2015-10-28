# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Cisco.SMB.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>[0-9a-f:]+)\s*$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
