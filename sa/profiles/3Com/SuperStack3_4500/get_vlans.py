# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3_4500.get_vlans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "3Com.SuperStack3_4500.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^\s*VLAN ID: (?P<vlan>\d+)$")
    rx_name = re.compile(r"^\s*Description: (?P<name>.+)$")

    def execute(self):
        r = []
        vlans = self.cli("display vlan all")
        vlans = vlans.splitlines()
        for i in range(len(vlans)):
            match_v = self.rx_vlan.search(vlans[i])
            if match_v:
                i += 1
                while not self.rx_name.search(vlans[i]):
                    i += 1
                match_n = self.rx_name.search(vlans[i])
                r.append({
                    "vlan_id": int(match_v.group("vlan")),
                    "name": match_n.group("name")
                    })
        return r
