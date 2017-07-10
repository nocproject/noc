# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
import re


class Script(BaseScript):
    name = "Siklu.EH.get_vlans"
    interface = IGetVlans
    rx_vlan = re.compile(
        r"^\s*\S+\s+(?P<vlanid>\d+)\s+\d+\s+\S+\s+\S+\s+\S+\s*\n",
        re.MULTILINE)

    def execute(self):
        r = []
        c = self.cli("show vlan\n")
        for match in self.rx_vlan.finditer(c):
            vlan_id = int(match.group('vlanid'))
            if vlan_id == 1:
                continue
            found = False
            for v in r:
                if v["vlan_id"] == vlan_id:
                    found = True
                    break
            if not found:
                r += [{"vlan_id": vlan_id}]
        return r
