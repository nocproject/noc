# ---------------------------------------------------------------------
# DLink.DxS.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "DLink.DxS.get_vlans"
    interface = IGetVlans

    def execute_cli(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
            if v["vlan_name"]:
                r += [{"vlan_id": v["vlan_id"], "name": v["vlan_name"]}]
            else:
                r += [{"vlan_id": v["vlan_id"]}]
        return r
