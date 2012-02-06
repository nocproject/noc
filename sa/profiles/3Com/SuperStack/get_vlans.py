# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## 3Com.SuperStack.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetVlans
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "3Com.SuperStack.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)[\s\t]+\d+[\s\t]+(?P<name>.*?)\s*$",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        vlans = self.cli("bridge vlan summary all")
        r = []
        for match in self.rx_vlan.finditer(vlans):
            r += [{
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
                }]
        return r
