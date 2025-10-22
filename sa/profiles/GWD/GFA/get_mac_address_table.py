# ---------------------------------------------------------------------
# GWD.GFA.get_mac_address_table
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
    name = "GWD.GFA.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile(
        r"^(?:\s+|\*)(?P<mac>\S+)\s+(?P<vlan>\S+)\s+(?P<port>(?:\d+/\d+|CPU))\s*(?:Static)?\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        v = self.scripts.get_vlans()
        vlans = {}
        for i in v:
            vlans[i["name"]] = i["vlan_id"]
        c = "show forward-entry"
        if mac is not None:
            c += " mac %s" % mac
        if vlan is not None:
            for i in v:
                if i["vlan_id"] == vlan:
                    c += " vlan %s" % i["name"]
                    break
        v = self.cli(c, cached=True)
        for match in self.rx_mac.finditer(v):
            r += [
                {
                    "vlan_id": vlans[match.group("vlan")],
                    "mac": match.group("mac"),
                    "interfaces": [match.group("port")],
                    "type": "C" if match.group("port") == "CPU" else "D",
                }
            ]
        return r
