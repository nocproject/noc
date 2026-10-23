# ---------------------------------------------------------------------
# Eltex.ME24xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES24xx.get_mac_address_table"
    interface = IGetMACAddressTable

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += f" address {mac}"
        if interface is not None:
            cmd += f" interface {interface}"
        if vlan is not None:
            cmd += f" vlan {vlan}"
        v = self.cli(cmd)
        for i in parse_table(v, expand_columns=True, max_width=80):
            r.append(
                {
                    "vlan_id": i[0],
                    "mac": i[1],
                    "interfaces": [i[4]],
                    "type": {"Learnt": "D", "Static": "C"}[i[2]],
                }
            )
        return r
