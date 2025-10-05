# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.ihasvlan import IHasVlan


class Script(BaseScript):
    name = "Generic.has_vlan"
    interface = IHasVlan
    requires = ["get_vlans"]

    def execute(self, vlan_id):
        return any(v["vlan_id"] == vlan_id for v in self.scripts.get_vlans())
