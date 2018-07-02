# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UPVEL.UP.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "UPVEL.UP.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        "^\s*(?P<vlan_id>\d+)\s{2,5}(?P<name>\S*)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            vlan_id = int(match.group("vlan_id"))
            if vlan_id == 1:
                continue
            name = match.group("name")
            if name:
                r += [{"vlan_id": vlan_id, "name": name}]
            else:
                r += [{"vlan_id": vlan_id}]
        return r
