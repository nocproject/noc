# ---------------------------------------------------------------------
# Dell.Powerconnect55xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<type>\S+)\s*$",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if interface is not None:
            cmd += f" interface {interface}"
        if vlan is not None:
            cmd += f" vlan {int(vlan)}"
        if mac is not None:
            cmd += f" address {int(vlan)}"
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            interface = match.group("interface")
            if interface == "0":
                continue
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interface],
                    "type": {"dynamic": "D", "static": "S"}[match.group("type").lower()],
                }
            )
        return r
