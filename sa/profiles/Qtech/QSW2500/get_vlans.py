# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_vlans
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
    name = "Qtech.QSW2500.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^\s*(?P<vlanid>\d+)\s+", re.MULTILINE)

    def execute_cli(self):
        r = []
        v = self.cli("show vlan")
        for match in self.rx_vlan.finditer(v):
            r += [{"vlan_id": int(match.group("vlanid"))}]
        return r
