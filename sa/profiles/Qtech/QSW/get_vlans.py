# ---------------------------------------------------------------------
# Qtech.QSW.get_vlans
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetvlans import IGetVlans


class Script(BaseScript):
    name = "Qtech.QSW.get_vlans"
    interface = IGetVlans

    rx_vlan = re.compile(
        r"^(?:VLAN name\s+:\s*(?P<name>\S+).|)VLAN ID\s+:\s*(?P<vlan_id>\d+)$",
        re.DOTALL | re.MULTILINE,
    )
    rx_vlan1 = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<name>\S+)\s+(?:Static|Dynamic)\s+ENET", re.DOTALL | re.MULTILINE
    )

    def execute(self):
        r = []
        # Try snmp first

        """
        # SNMP Not working!
        if self.has_snmp():
            try:
                for vlan, name in self.snmp.join_tables(
                    "1.3.6.1.2.1.17.7.1.4.2.1.3",
                    "1.3.6.1.2.1.17.7.1.4.3.1.1"):
                    if name == "":
                        name = "Vlan-" + vlan
                    r.append({
                        "vlan_id": vlan,
                        "name": name
                        })
                return r
            except self.snmp.TimeOutError:
                pass
        """

        # Fallback to CLI
        v = self.cli("show vlan")
        for match in self.rx_vlan.finditer(v):
            vlan_id = match.group("vlan_id")
            name = match.group("name")
            if not name:
                r.append({"vlan_id": int(vlan_id)})
            else:
                r += [match.groupdict()]
        if r == []:
            for match in self.rx_vlan1.finditer(v):
                vlan_id = match.group("vlan_id")
                name = match.group("name")
                if not name:
                    r.append({"vlan_id": int(vlan_id)})
                else:
                    r += [match.groupdict()]

        return r
