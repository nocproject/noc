# ---------------------------------------------------------------------
# DLink.DxS_Smart.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
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
        # DXS-1210-10TS has different OID for vlans
        f_oid = pmib + ".7.6.1.1"
        if pmib == "1.3.6.1.4.1.171.10.139.2.1":
            f_oid = pmib + ".4.2.2.1.1"
        for oid, v in self.snmp.getnext(f_oid, bulk=True):  # dot1qVlanFdbId
            r += [{"vlan_id": oid.split(".")[-1], "name": v}]
        return r

    def execute_cli(self):
        r = []
        vlans = self.profile.get_vlans(self)
        for v in vlans:
            r += [{"vlan_id": v["vlan_id"], "name": v["vlan_name"]}]
        return r
