# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "AlliedTelesis.AT8000.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        r = []
        v = self.cli("show vlan", cached=True)
        for match in self.profile.rx_vlan.finditer(v):
            r += [{"vlan_id": match.group("vlan_id"), "name": match.group("name")}]
        return r
