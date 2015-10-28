# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re

rx_vlan_line = re.compile(
    r"^\s*(?P<vlan_id>\d{1,4})(\s+\S+){9}\s+o(?:n|ff)\s+(?P<name>(\S+\s*)+?)"
    r"\s*$")
rx_vlan1_line = re.compile(
    r"^\s*(?P<vlan_id>\d{1,4})(\s+\S+){9}\s+(?P<name>(\S+\s*)+?)\s*$")


class Script(BaseScript):
    name = "Alcatel.AOS.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = rx_vlan_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id": int(match.group("vlan_id")),
                    "name": match.group("name")
                })
            else:
                match = rx_vlan1_line.match(l.strip())
                if match:
                    r.append({
                        "vlan_id": int(match.group("vlan_id")),
                        "name": match.group("name")
                    })
        return r
