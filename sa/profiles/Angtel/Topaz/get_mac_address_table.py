# ---------------------------------------------------------------------
# Angtel.Topaz.get_mac_address_table
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
    name = "Angtel.Topaz.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<iface>\S+)\s+(?P<type>\S+)", re.MULTILINE
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac address-table"
        if mac is not None:
            cmd += "address %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
            if match.group("iface") == "0":
                continue
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("iface")],
                    "type": {"dynamic": "D", "static": "S", "self": "C", "secure": "S"}[
                        match.group("type").lower()
                    ],
                }
            ]
        return r
