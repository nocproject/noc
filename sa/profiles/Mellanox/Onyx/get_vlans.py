# ---------------------------------------------------------------------
# Mellanox.Onyx.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Mellanox.Onyx.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(r"^(?P<vlan_id>\d+)\s+(?P<name>\S+)", re.MULTILINE)

    def execute_cli(self):
        r = []
        v = self.cli("show vlan")
        for match in self.rx_vlan.finditer(v):
            r += [match.groupdict()]
        return r
