# ----------------------------------------------------------------------
# Alcatel.OS62xx.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Alcatel.OS62xx.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge address-table"
        if vlan:
            cmd += f" vlan {int(vlan)}"
        if mac:
            cmd += f" address {mac}"
        if interface:
            if interface.lower().startswith("po"):
                cmd += f" port-channel {interface}"
            else:
                cmd += f" ethernet {interface}"
        r = []
        for v, m, port, type in parse_table(self.cli(cmd)):
            r.append(
                {
                    "vlan_id": v,
                    "mac": m,
                    "interfaces": [port],
                    "type": {"dynamic": "D", "static": "S"}[type.lower()],
                }
            )
        return r
