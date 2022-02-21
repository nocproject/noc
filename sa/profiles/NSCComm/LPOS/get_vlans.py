# ---------------------------------------------------------------------
# NSCComm.LPOS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "NSCComm.LPOS.get_vlans"
    interface = IGetVlans
    cache = True

    rx_vlan = re.compile(r"^\s*(?P<vlan_id>\d+)", re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("vlan", cached=True)
        for match in self.rx_vlan.finditer(v):
            vid = int(match.group("vlan_id"))
            if vid == 1:
                continue
            r += [{"vlan_id": vid}]
        return r
