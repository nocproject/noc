# ---------------------------------------------------------------------
# DLink.DGS3100.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.sa.profiles.DLink.DGS3100.profile import DGS3100


class Script(BaseScript):
    name = "DLink.DGS3100.get_mac_address_table"
    interface = IGetMACAddressTable

    always_prefer = "S"

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+\S+\s+(?P<mac>\S+)\s+"
        r"(?P<interfaces>\S+)\s+(?P<type>\S+)\s*(\S*\s*)?$",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        # Fallback to CLI
        cmd = "show fdb"
        if mac is not None:
            cmd += f" mac_address {mac}"
        if interface is not None:
            cmd += f" port {interface}"
        if vlan is not None:
            if self.match_version(DGS3100, version__gte="3.60.30"):
                cmd += f" vlanid {int(vlan)}"
            else:
                for v in self.scripts.get_vlans():
                    if v["vlan_id"] == vlan:
                        cmd += f" vlan {v['name']}"
                        break
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "dynamic": "D",
                        "static": "S",
                        "deleteontimeout": "D",
                        "deleteonreset": "D",
                        "permanent": "S",
                        "self": "S",
                    }[match.group("type").lower()],
                }
            )
        return r
