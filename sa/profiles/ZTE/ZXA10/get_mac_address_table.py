# ---------------------------------------------------------------------
# ZTE.ZXA10.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.core.mac import MAC


class Script(BaseScript):
    name = "ZTE.ZXA10.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_mac = re.compile(
        r"^(?P<mac>\S+[0-9a-f\.]+)\s+(?P<vlan_id>\d+).*(?P<type>Dynamic)\s+(?P<interface>\S+)",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac"
        # if interface is not None:
        #    cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if mac is not None:
            cmd += " %s" % MAC(mac).to_cisco()
        r = []
        for match in self.rx_mac.finditer(self.cli(cmd)):
            if match.group("type") == "N/A":
                continue
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interface")],
                    "type": {"Dynamic": "D", "Static": "S"}[match.group("type")],
                }
            ]
        return r
