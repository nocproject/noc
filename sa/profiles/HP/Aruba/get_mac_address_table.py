# ---------------------------------------------------------------------
# HP.Aruba.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript


class Script(BaseScript):
    name = "HP.Aruba.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac_table = re.compile(
        r"(?P<mac>\S+)\s+(?P<vlan>\d+)\s+(?P<type>dynamic|static)\s+(?P<port>\S+)"
    )

    def execute_cli(self, **kwargs):
        r = []
        v = self.cli("show mac-address-table")
        for mac, vlan, m_type, port in self.rx_mac_table.findall(v):
            r += [
                {
                    "vlan_id": vlan,
                    "mac": mac,
                    "interfaces": [port],
                    "type": m_type[0].upper(),
                }
            ]
        return r
