# ---------------------------------------------------------------------
# Brocade.IronWare.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Brocade.IronWare.get_vlans"
    interface = IGetVlans

    rx_vlan_line = re.compile(r"^\S+\s(?P<vlan_id>\d+)\,\sName\s(?P<name>[A-Za-z0-9\-\_]+?),.+$")

    def execute_cli(self):
        vlans = self.cli("show vlans")
        r = []
        for match in self.rx_vlan_line.finditer(vlans):
            vlan_id = int(match.group("vlan_id"))
            name = match.group("name")
            if name == "[None]":
                r += [{"vlan_id": vlan_id}]
            else:
                r += [{"vlan_id": vlan_id, "name": name}]
        return r
