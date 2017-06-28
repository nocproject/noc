# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.DSLAM.get_vlans
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
    name = "Eltex.DSLAM.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile("^(?P<vlan_id>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        cmd = self.cli("switch show vlan table all", cached=True)
        for match in self.rx_vlan.finditer(cmd):
            r += [{
                "vlan_id": match.group("vlan_id")
            }]
        return r
