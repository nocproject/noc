# ---------------------------------------------------------------------
# Eltex.PON.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2014 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Eltex.PON.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_olt = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>(\S+ \d+|\S+))\s+"
        r"(?P<type>\S+)\s+\S+\s+\S+\s+\d+\s*$",
        re.MULTILINE,
    )

    rx_switch = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>(\S+ \d+|\S+))\s+"
        r"(?P<type>\S+)\s+\S+\s+\S+\s+\d+\s*$",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        r = []

        # Fallback to CLI
        # PON ports
        cmd = "show mac table"
        if interface is not None:
            cmd += " %s" % interface
        else:
            cmd += " x"
        for match in self.rx_olt.finditer(self.cli(cmd)):
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
        # Switch ports
        cmd = "show mac"
        if vlan is not None:
            cmd += " include vlan %s" % vlan
        elif interface is not None:
            cmd += " include interface %s" % interface
        elif mac is not None:
            cmd += " include mac %s" % self.profile.convert_mac(mac)
        cmd += "\r"
        with self.profile.switch(self):
            for match in self.rx_switch.finditer(self.cli(cmd)):
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
