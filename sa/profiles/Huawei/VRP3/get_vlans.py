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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "Huawei.VRP3.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(r"^\s+(?P<vlanid>\d+)\s+\d+\s+\d+\s+\S+",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan all")):
            r.append({"vlan_id": int(match.group('vlanid'))})
        return r
