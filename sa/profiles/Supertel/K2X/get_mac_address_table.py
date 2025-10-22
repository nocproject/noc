# ---------------------------------------------------------------------
# Supertel.K2X.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Supertel.K2X.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>\S+)\s+(?P<type>\S+)\s*$",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []

        # Fallback to CLI
        cmd = "show bridge address-table"
        if vlan is not None:
            cmd += " vlan %s" % vlan
        if interface is not None:
            if interface[:1] == "g":
                cmd += " ethernet %s" % interface
            elif interface[:2] == "ch":
                cmd += " port-channel %s" % interface
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        for match in self.rx_line.finditer(self.cli(cmd)):
            interfaces = match.group("interfaces")
            if interfaces == "0":
                continue
            r.append(
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [interfaces],
                    "type": {"dynamic": "D", "static": "S", "permanent": "S", "self": "S"}[
                        match.group("type").lower()
                    ],
                }
            )
        return r
