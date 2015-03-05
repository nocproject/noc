# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## OS.Linux.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
import re
## Python modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "OS.Linux.get_vlans"
    implements = [IGetVlans]

    rx_vlan = re.compile(
        r"^(?P<interface>\S+)\s+\|+\s+(?P<vlan>\d+)\s+\|+\s+\S+$",
        re.MULTILINE)

    def execute(self):
        r = []
        vconfig = self.cli("cat /proc/net/vlan/config")
        for vlan in self.rx_vlan.finditer(vconfig):
            vlan_id = vlan.group("vlan")
            if {"vlan_id": vlan_id} not in r:
                r.append({"vlan_id": vlan_id})
        if not r:
            raise Exception("Not implemented")
        return r
