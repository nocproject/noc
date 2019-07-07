# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^\s+(?P<vlans>\d+\S*\d*)\s*\n", re.MULTILINE)

    def execute_cli(self):
        r = []
        v = self.cli("show vlan")
        match = self.rx_vlan.search(v)
        vlans = self.expand_rangelist(match.group("vlans"))
        for i in vlans:
            r += [{"vlan_id": int(i)}]
        return r
