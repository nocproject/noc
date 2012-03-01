# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_vlans
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
import re


class Script(NOCScript):
    name = "Huawei.VRP3.get_vlans"
    implements = [IGetVlans]
    rx_vlan = re.compile(r"^\s+(?P<vlanid>\d+)\s+\d+\s+\d+\s+\S+",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan all")):
            r.append({"vlan_id": int(match.group('vlanid'))})
        return r
