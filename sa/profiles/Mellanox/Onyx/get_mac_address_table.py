# ----------------------------------------------------------------------
# Mellanox.Onyx.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Mellanox.Onyx.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+(?P<interfaces>\S+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        v = self.cli(cmd)
        for match in self.rx_line.finditer(v):
            iface = match.group("interfaces")
            # if iface == '0':
            #    continue
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [iface],
                    "type": {"Dynamic": "D", "Static": "S"}[
                        match.group("type")
                    ],
                }
            )
        return r
