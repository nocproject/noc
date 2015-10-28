# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.CatOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re

rx_vlan_line = re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+[a-zA-Z]")


class Script(BaseScript):
    name = "Cisco.1900.get_vlans"
    interface = IGetVlans

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.split("\n"):
            match = rx_vlan_line.match(l.strip())
            if match:
                name = match.group("name")
                vlan_id = int(match.group("vlan_id"))
                if vlan_id >= 1000 and vlan_id <= 1005 \
                and name in [
                    "fddi-default", "token-ring-defau", "fddinet-default",
                    "trnet-default"
                ]:
                    continue
                r.append({
                    "vlan_id": vlan_id,
                    "name": name
                })
        return r
