# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Nortel.BayStack425.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "Nortel.BayStack425.get_vlans"
    implements = [IGetVlans]

    rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>.+)\s+"
                              r"(Port)\s+\S+\s+\S+\s+\S+\s+\S+$")

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = self.rx_vlan_line.match(l.strip())
            if match:
                name = match.group("name").strip()
                vlan_id = int(match.group("vlan_id"))
                r += [{
                    "vlan_id": vlan_id,
                    "name": name
                }]
        return r
