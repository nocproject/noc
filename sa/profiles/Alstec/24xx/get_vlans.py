# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Alstec.24xx.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^vlan database\s*\n"
        r"^vlan (?P<vlans>\S+)\s*\n"
        r"(vlan name \d \"\S+\"\s*\n)*"
        r"exit\s*\n", re.MULTILINE)

    def execute(self):
        r = []
        match = self.rx_vlan.search(self.scripts.get_config())
        for vlan_id in self.expand_rangelist(match.group("vlans")):
            r += [{"vlan_id": vlan_id}]
        return r
