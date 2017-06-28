# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MBAN.get_vlans
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
    name = "Iskratel.MBAN.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile(
        r"^\s+(?P<id>\d+)\s+(?P<name>.+)?\s+\d+\s*\n", re.MULTILINE)

    def execute(self):
        r = []
        c = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(c):
            if match.group('id') == "1":
                continue
            d = {}
            d["vlan_id"] = int(match.group('id'))
            if match.group('name'):
                d["name"] = match.group('name').strip()
            r += [d]
        return r
