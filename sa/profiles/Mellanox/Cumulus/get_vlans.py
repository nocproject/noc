# ---------------------------------------------------------------------
# Mellanox.Cumulus.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans
from noc.core.text import parse_table
from noc.core.validators import is_vlan


class Script(BaseScript):
    name = "Mellanox.Cumulus.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        a = []
        v = self.cli("net show bridge vlan", cached=True)
        for i in parse_table(v):
            if is_vlan(i[1]) and not int(i[1]) in a:
                a += [int(i[1])]
        return [{"vlan_id": int(i)} for i in a]
