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
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "f5.BIGIP.get_vlans"
    cache = True
    interface = IGetVlans

    rx_tag = re.compile("Tag\s+(?P<tag>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show /net vlan -hidden")
        for h, data in self.parse_blocks(v):
            if h.startswith("Net::Vlan: "):
                match = self.rx_tag.search(data)
                if match:
                    r += [{
                        "vlan_id": match.group("tag"),
                        "name": h[11:]
                    }]
        return r
