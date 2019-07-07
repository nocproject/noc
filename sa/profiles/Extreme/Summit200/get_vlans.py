# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Extreme.Summit200.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^(?P<name>\S+)\s+(?P<vlan_id>\d{1,4})\s", re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            r += [match.groupdict()]
        return r
