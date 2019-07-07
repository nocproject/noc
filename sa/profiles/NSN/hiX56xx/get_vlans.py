# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSN.hiX56xx.get_vlans
# sergey.sadovnikov@gmail.com
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "NSN.hiX56xx.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile(r"^\s(?P<vlan_id>\d+)\s+\|\s+(?P<name>\S+)$", re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show vlan properties", cached=True)
        for match in self.rx_vlan.finditer(v):
            if match.group("name") == "<noname>":
                r += [{"vlan_id": match.group("vlan_id")}]
            else:
                r += [match.groupdict()]
        return r
