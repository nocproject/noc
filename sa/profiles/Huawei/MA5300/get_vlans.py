# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.MA5300.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Huawei.MA5300.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"Vlan ID: (?P<vlanid>\d+)",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan all")):
            vlan_id = int(match.group("vlanid"))
            r += [{
                    "vlan_id": vlan_id
                }]
        return r

