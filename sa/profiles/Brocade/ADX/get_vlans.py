# ---------------------------------------------------------------------
# Brocade.ADX.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Brocade.ADX.get_vlans"
    interface = IGetVlans

    rx_vlan_line = re.compile(r"^\S+\s(?P<vlan_id>\d+)\,\sName\s(?P<name>[A-z0-9\-\_]+?),.+$")

    def execute(self):
        vlans = self.cli("show vlan")
        r = []
        for l in vlans.splitlines():
            match = self.rx_vlan_line.match(l.strip())
            if match:
                vlan_id = int(match.group("vlan_id"))
                name = match.group("name")
                if name == "[None]":
                    r += [{"vlan_id": vlan_id}]
                else:
                    r += [{"vlan_id": vlan_id, "name": name}]

        return r
