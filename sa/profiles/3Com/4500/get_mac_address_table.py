# ---------------------------------------------------------------------
# 3Com.4500.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "3Com.4500.get_mac_address_table"
    interface = IGetMACAddressTable

    always_prefer = "C"

    rx_line = re.compile(
        r"^(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s+(?P<interfaces>\S+)\s+\S+$",
        re.MULTILINE,
    )

    def execute_snmp(self, interface=None, vlan=None, mac=None, **kwargs):
        # No mac adresses....
        raise NotImplementedError

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        cmd = "display mac-address"
        r = []

        if mac is not None:
            mac = self.profile.convert_mac(mac)
            mac = mac.replace(":", "")
            mac = mac[0:4] + "-" + mac[4:8] + "-" + mac[8:]
            cmd += " %s" % mac
        if interface is not None:
            interface = interface.replace("Po ", "Bridge-Aggregation")
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan

        # Fallback to CLI
        for match in self.rx_line.finditer(self.cli(cmd)):
            iface = match.group("interfaces")
            iface = iface.replace("GigabitEthernet", "Gi ")
            iface = iface.replace("Bridge-Aggregation", "Po ")
            if iface == "0":
                continue
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [iface],
                    "type": {"learned": "D", "static": "S", "permanent": "S", "self": "S"}[
                        match.group("type").lower()
                    ],
                }
            ]

        return r
