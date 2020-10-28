# ---------------------------------------------------------------------
# Eltex.MES.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_vlans import Script as BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Eltex.MES.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<name>.+?)\s+(\S+|)\s+\S+\s+\S+\s*$", re.MULTILINE
    )

    def execute_cli(self, **kwargs):
        r = []
        for match in self.rx_vlan.finditer(self.cli("show vlan")):
            if match.group("name") != "-":
                r += [match.groupdict()]
            else:
                r += [{"vlan_id": int(match.group("vlan_id"))}]
        return r
