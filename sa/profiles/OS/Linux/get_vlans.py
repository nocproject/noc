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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "OS.Linux.get_vlans"
    interface = IGetVlans

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
