# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.MES24xx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Eltex.MES24xx.get_vlans"
    interface = IGetVlans

    rx_vlan_id = re.compile(r"^Vlan ID\s+: (?P<vlan_id>\d+)\s*\n", re.MULTILINE)
    rx_vlan_name = re.compile(r"^Name\s+: (?P<name>\S+)\s*\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        for vlan in self.cli("show vlan", cached=True).split("---"):
            match = self.rx_vlan_id.search(vlan)
            if match:
                vlan_id = match.group("vlan_id")
                match = self.rx_vlan_name.search(vlan)
                if match:
                    r += [{"vlan_id": vlan_id, "name": match.group("name")}]
                else:
                    r += [{"vlan_id": vlan_id}]
        return r
