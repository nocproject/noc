# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SMB.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Cisco.SMB.get_vlans"
    interface = IGetVlans

    rx_vlan_line = re.compile(
        r"^\s*(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+.*$", re.MULTILINE)

    def extract_vlans(self, data):
        return [
            {
                "vlan_id": int(match.group("vlan_id")),
                "name": match.group("name")
            }
            for match in self.rx_vlan_line.finditer(data)
        ]

    @BaseScript.match()
    def execute_vlan_brief(self):
        vlans = self.cli("show vlan")
        return self.extract_vlans(vlans)
