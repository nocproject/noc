# ---------------------------------------------------------------------
# HP.Aruba.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "HP.Aruba.get_vlans"
    interface = IGetVlans

    def execute_snmp(self):
        r = []
        for vlan, name in self.snmp.join_tables(
            "1.3.6.1.2.1.17.7.1.4.2.1.3", "1.3.6.1.2.1.17.7.1.4.3.1.1"
        ):
            r.append({"vlan_id": vlan, "name": name})
        return r
