# ---------------------------------------------------------------------
# DLink.DxS.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "DLink.DxS.get_switchport"
    interface = IGetSwitchport

    def execute(self):
        ports = self.profile.get_ports(self)
        vlans = self.profile.get_vlans(self)
        interfaces = []

        for p in ports:
            iface = p["port"]
            i = {
                "interface": iface,
                "status": p["status"],
                "members": [],
                "802.1Q Enabled": True,
                "tagged": [v["vlan_id"] for v in vlans if iface in v["tagged_ports"]],
            }
            desc = p["desc"]
            if desc and desc != "null":
                i["description"] = desc
            untagged = [v["vlan_id"] for v in vlans if iface in v["untagged_ports"]]
            if untagged:
                i["untagged"] = untagged[0]
            interfaces += [i]
        return interfaces
