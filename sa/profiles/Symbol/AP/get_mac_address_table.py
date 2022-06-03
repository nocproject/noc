# ---------------------------------------------------------------------
# Symbol.AP.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Symbol.AP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile(
        r"^\d+\s+(?P<vlan_id>\d+)\s+(?P<interface>\S+)\s+(?P<mac>\S+)\s+forward", re.MULTILINE
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        c = self.cli("show mac-address-table")
        for match in self.rx_mac.finditer(c):
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": "D",
                }
            ]
        return r
