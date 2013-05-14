# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Ubiquiti.AirOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Ubiquiti.AirOS.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"vlan.\d+.id=(?P<vlan>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("cat /tmp/system.cfg")):
            r += [{"vlan_id": int(match.group("vlan"))}]
        return r
