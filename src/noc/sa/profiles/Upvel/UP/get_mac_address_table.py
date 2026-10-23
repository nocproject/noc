# ---------------------------------------------------------------------
# Upvel.UP.get_mac_address_table
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
    name = "Upvel.UP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<type>\S+)\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<iface>\S+ \S+)\s*$",
        re.MULTILINE,
    )

    """
    Ignoring lines like these. This are invalid mac addreses

Type    VID  MAC Address        Ports
Static  35   33:33:00:00:00:01  GigabitEthernet 1/1-8 2.5GigabitEthernet 1/1-2 10GigabitEthernet 1/1-2 CPU
Static  35   33:33:00:00:00:02  GigabitEthernet 1/1-8 2.5GigabitEthernet 1/1-2 10GigabitEthernet 1/1-2 CPU
Static  35   33:33:ff:01:62:5a  GigabitEthernet 1/1-8 2.5GigabitEthernet 1/1-2 10GigabitEthernet 1/1-2 CPU
Static  35   ff:ff:ff:ff:ff:ff  GigabitEthernet 1/1-8 2.5GigabitEthernet 1/1-2 10GigabitEthernet 1/1-2 CPU

    """

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac address-table"
        if mac is not None:
            cmd += f"address {mac}"
        if interface is not None:
            cmd += f" interface {interface}"
        if vlan is not None:
            cmd += f" vlan {vlan}"
        for match in self.rx_line.finditer(self.cli(cmd)):
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("iface")],
                    "type": {"dynamic": "D", "static": "S", "self": "C", "secure": "S"}[
                        match.group("type").lower()
                    ],
                }
            )
        return r
