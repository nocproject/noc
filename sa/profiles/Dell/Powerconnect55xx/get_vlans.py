# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(r"^(?P<vlan_id>\d+)\s+(?P<vlan_name>\S+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            r += [{
                "vlan_id": match.group('vlan_id'),
                "name": match.group('vlan_name')
            }]
        return r
