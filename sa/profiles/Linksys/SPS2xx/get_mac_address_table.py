# ---------------------------------------------------------------------
# Linksys.SPS2xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Linksys.SPS2xx.get_mac_address_table"
    interface = IGetMACAddressTable
    cached = True

    always_prefer = "S"

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)", re.MULTILINE
    )

    def execute_cli(self, interface=None, vlan=None, mac=None, **kwargs):
        r = []
        # Fallback to CLI
        cmd = "show mac address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd, cached=True)):
            interfaces = match.group("interfaces")
            if interfaces == "0":
                continue
            if interface is not None:
                if interfaces == interface:
                    r += [
                        {
                            "vlan_id": match.group("vlan_id"),
                            "mac": match.group("mac"),
                            "interfaces": [interfaces],
                            "type": {"dynamic": "D", "static": "S", "permanent": "S", "self": "S"}[
                                match.group("type").lower()
                            ],
                        }
                    ]
            else:
                r += [
                    {
                        "vlan_id": match.group("vlan_id"),
                        "mac": match.group("mac"),
                        "interfaces": [interfaces],
                        "type": {"dynamic": "D", "static": "S", "permanent": "S", "self": "S"}[
                            match.group("type").lower()
                        ],
                    }
                ]
        return r
