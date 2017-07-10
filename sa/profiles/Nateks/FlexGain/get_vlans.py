# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.FlexGain.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2010 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "Nateks.FlexGain.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^(?P<vlan_id>\d+)\s+", re.MULTILINE)

    def execute(self):
        r = []
        vlans = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            vlan_id = int(match.group("vlan_id"))
            if (vlan_id == 1) or (vlan_id in vlans):
                continue
            r += [{
                "vlan_id": int(match.group("vlan_id"))
            }]
            vlans += [vlan_id]
        return r
