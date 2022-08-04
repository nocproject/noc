# ----------------------------------------------------------------------
# Mellanox.Cumulus.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.validators import is_vlan


class Script(BaseScript):
    name = "Mellanox.Cumulus.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<iface>\S+)\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>yes|no)",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        v = self.cli("brctl showmacs bridge")
        for match in self.rx_line.finditer(v):
            if not is_vlan(match.group("vlan_id")):
                # In some cases may be 0
                continue
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("iface")],
                "type": {"no": "D", "yes": "C"}[match.group("type")],
            }]
        return r
