# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Intracom.UltraLink.get_vlans
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
    name = "Intracom.UltraLink.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^(?P<vid>\d+)\s+(?P<name>\S*)\s*$", re.MULTILINE)

    def execute_cli(self, **kwargs):
        vlans = []
        cli = self.cli("get bridge vlan")
        for match in self.rx_vlan.finditer(cli):
            vlan_id = int(match.group("vid"))
            name = match.group("name")
            if name == "":
                name = "VLAN%d" % vlan_id
            vlans += [{"vlan_id": vlan_id, "name": name}]
        return vlans
