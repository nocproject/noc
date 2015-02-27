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
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID


class Script(NOCScript):
    name = "Cisco.SMB.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac = re.compile(r"^System MAC Address:\s+(?P<mac>[0-9a-f:]+)\s*$", re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show system")
        match = self.re_search(self.rx_mac, v)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
