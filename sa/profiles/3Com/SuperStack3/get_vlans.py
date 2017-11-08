# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_vlans
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

from noc.core.script.base import BaseScript
# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "3Com.SuperStack3.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<name>\S+)?\s*\n",
        re.MULTILINE)

    def execute(self):
        vlans = self.cli("bridge vlan summary all")
        r = []
        for match in self.rx_vlan.finditer(vlans):
            if match.group("vlan_id") == "1":
                continue
            if match.group("name"):
                r += [{
                    "vlan_id": int(match.group("vlan_id")),
                    "name": match.group("name").strip()
                }]
            else:
                r += [{
                    "vlan_id": int(match.group("vlan_id"))
                }]
        return r
