# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans


class Script(NOCScript):
    name = "f5.BIGIP.get_vlans"
    cache = True
    implements = [IGetVlans]

    rx_vlan = re.compile(r"^VLAN\s+(?P<name>.+?)(?:\s+\([^)]+\))?\s+tag\s+(?P<tag>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        for match in self.rx_vlan.finditer(self.cli("b vlan show")):
            r += [{
                "name": match.group("name"),
                "vlan_id": match.group("tag")
            }]
        return r
