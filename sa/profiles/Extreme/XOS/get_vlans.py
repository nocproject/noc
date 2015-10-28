# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re

rx_vlan_line = re.compile(r"^(?P<name>\S+)\s+(?P<vlan_id>\d{1,4})\s")


class Script(BaseScript):
    name = "Extreme.XOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = rx_vlan_line.match(l.strip())
            if match:
                name = match.group("name")
                vlan_id = int(match.group("vlan_id"))
                r.append({
                    "vlan_id": vlan_id,
                    "name": name
                    })
        return r
