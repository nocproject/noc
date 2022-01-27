# ---------------------------------------------------------------------
# CData.xPON.get_mac_address_table
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
    name = "CData.xPON.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?:\-|\d+)\s+(?P<interface>[xgpl]\S+\d)\s+"
        r"(?:\-|\d+)\s+(?:\-|\d+)\s+(?P<type>dynamic|static)\s*\n",
        re.MULTILINE,
    )
    rx_line2 = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<interface>[xgpl]\S+\d)\s+(?P<type>dynamic|static)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        r = []
        with self.configure():
            cmd = "show mac-address "
            if interface is not None:
                cmd += "port %s" % interface
            elif vlan is not None:
                cmd += "vlan %s" % vlan
            else:
                cmd += "all"
            v = self.cli(cmd)
            for match in self.rx_line.finditer(v):
                if mac is not None:
                    if match.group("mac") != mac:
                        continue
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interface")],
                        "type": {"dynamic": "D", "static": "S"}[match.group("type").lower()],
                    }
                ]
            if len(r) == 0:
                for match in self.rx_line2.finditer(v):
                    if mac is not None:
                        if match.group("mac") != mac:
                            continue
                    r += [
                        {
                            "vlan_id": match.group("vlan_id"),
                            "mac": match.group("mac"),
                            "interfaces": [match.group("interface")],
                            "type": {"dynamic": "D", "static": "S"}[match.group("type").lower()],
                        }
                    ]
        return r
