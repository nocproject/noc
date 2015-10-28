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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Ubiquiti.AirOS.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(r"vlan.\d+.id=(?P<vlan>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("cat /tmp/system.cfg")):
            r += [{"vlan_id": int(match.group("vlan"))}]
        return r
