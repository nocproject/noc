# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_vlans
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
    name = "Alstec.7200.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^(?P<vlan_id>\d+)\s*(?P<name>\S+)?\s*(Static|Dynamic)\s*\n",
        re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            if match.group("name"):
                r.append(match.groupdict())
            else:
                r += [{"vlan_id": match.group("vlan_id")}]
        return r
