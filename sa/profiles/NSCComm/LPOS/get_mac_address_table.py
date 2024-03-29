# ---------------------------------------------------------------------
# NSCComm.LPOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "NSCComm.LPOS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s+\d+\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\d+\s+\S\s+(?P<port>\d+)", re.MULTILINE
    )
    types = {"learned": "D"}

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        if self.is_sprinter:
            raise NotImplementedError
        v = self.cli("mapmac -f")
        for match in self.rx_line.finditer(v):
            if match.group("type") in ["mcast", "bcast"]:
                continue
            if match.group("port") != "cpu":
                r += [
                    {
                        "vlan_id": 1,
                        "mac": match.group("mac"),
                        "interfaces": match.group("port"),
                        "type": self.types[match.group("type")],
                    }
                ]
            else:
                r += [
                    {
                        "vlan_id": 1,
                        "mac": match.group("mac"),
                        "interfaces": match.group("port"),
                        "type": "C",
                    }
                ]
        return r
