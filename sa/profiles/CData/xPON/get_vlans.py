# ---------------------------------------------------------------------
# CData.xPON.get_vlans
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
    name = "CData.xPON.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*Vlan-ID: (?P<vlan_id>\d+)\s+Vlan-Name: (?P<vlan_name>.+?)\s*\n", re.MULTILINE
    )

    def execute_cli(self):
        r = []
        with self.configure():
            v = self.cli("show vlan all")
            for match in self.rx_vlan.finditer(v):
                r += [match.groupdict()]
        return r
