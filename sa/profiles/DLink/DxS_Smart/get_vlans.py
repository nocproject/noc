# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "DLink.DxS_Smart.get_vlans"
    interface = IGetVlans
    always_prefer = "S"

    def execute_snmp(self):
        r = []
        pmib = self.profile.get_pmib(self.scripts.get_version())
        if pmib is None:
            raise NotImplementedError()
        for oid, v in self.snmp.getnext(pmib + ".7.6.1.1", bulk=True):  # dot1qVlanFdbId
            r += [{"vlan_id": oid.split(".")[-1], "name": v}]
        return r

    def execute_cli(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
            r += [{"vlan_id": v["vlan_id"], "name": v["vlan_name"]}]
        return r
