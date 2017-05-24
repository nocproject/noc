# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.ESR.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.ESR.get_vlans"
    interface = IGetVlans
    cache = True

    def execute(self):
        r = []
        c = self.cli("show vlan", cached=True)
        for vlan_id, name, tagged, untagged in parse_table(c):
            r += [{
                "vlan_id": vlan_id,
                "name": name,
            }]
        return r
