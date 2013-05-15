# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
from noc.sa.profiles.Arista.EOS import SSeries


class Script(NOCScript):
    name = "Arista.EOS.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_mac = re.compile(
        r"System MAC address:\s+(?P<mac>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show version")
        match = self.re_search(self.rx_mac, v)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
