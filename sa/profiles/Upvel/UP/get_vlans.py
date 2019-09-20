# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Upvel.UP.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Upvel.UP.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        r = []
        v = self.cli("show vlan")
        t = parse_table(v, allow_wrap=True)
        for i in t:
            vlan_id = int(i[0])
            if vlan_id == 1:
                continue
            name = i[1]
            if name:
                r += [{"vlan_id": vlan_id, "name": name}]
            else:
                r += [{"vlan_id": vlan_id}]
        return r
