# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Huawei.MA5300.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile(
        r"Now, the following vlan exist\(s\):\s*\n\s*(?P<vlans>.+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        r = []
        match = self.rx_vlan.search(self.cli("show vlan\n\n", cached=True))
        vlans = match.group("vlans").strip().replace("(default)", "")
        for vlan_id in self.expand_rangelist(vlans):
            r += [{
                "vlan_id": vlan_id
            }]
        return r
