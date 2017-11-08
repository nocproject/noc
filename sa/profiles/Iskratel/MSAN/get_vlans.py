# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.MSAN.get_vlans
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
    name = "Iskratel.MSAN.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile(
        r"^(?P<id>\d+)\s+(?P<name>\S+)?\s+\S+\s*",
        re.MULTILINE)

    def execute(self):
        r = []
        c = self.cli("show vlan brief", cached=True)
        for match in self.rx_vlan.finditer(c):
            if match.group('id') == "1":
                continue
            d = {}
            d["vlan_id"] = int(match.group('id'))
            if match.group('name'):
                d["name"] = match.group('name')
            r += [d]
        return r
