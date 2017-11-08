# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Qtech.QOS.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^(?P<vlanid>\d+)\s+", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            vlan_id = int(match.group('vlanid'))
            r += [{
                "vlan_id": int(match.group('vlanid'))
            }]
        return r
