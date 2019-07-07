# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# GWD.GFA.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC Modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "GWD.GFA.get_vlans"
    cache = True
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^Interface VLAN (?P<name>\S+) is \S+\.\s*\n"
        r"^\s+Physical status is \S+, administrator status is \S+\.\s*\n"
        r"(^\s+Interface description: .+?\s*\n)?"
        r"^\s+MTU \d+ bytes\.\s*\n"
        r"(^\s+IP address:\s*\n)?"
        r"(^\s+\S+\s*\n)?"
        r"^\s+IP binding \S+\.\s*\n"
        r"^\s+MulitiCast Flood Mode is \d+\.\s*\n"
        r"^\s+Vlan id is (?P<vlan_id>\d+)\.\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        r = []
        vlans = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(vlans):
            r += [match.groupdict()]
        return r
