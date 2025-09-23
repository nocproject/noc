# ---------------------------------------------------------------------
# Juniper.JUNOS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2025 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_mac_address_table import Script as BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Juniper.JUNOS.get_mac_address_table"
    interface = IGetMACAddressTable

    always_prefer = "C"
    # rx_line = re.compile(
    #     r"(?P<vlan_name>[^ ]+)\s+(?P<mac>[^ ]+)\s+"
    #     r"(?P<type>Learn|Static|S|D|L|P)(?:,SE)?\s+"
    #     r"[^ ]+\s+(?P<interfaces>.*?)(?:\s+\d+\s+\d+)?$"
    # )
    rx_line = re.compile(
        r"(?P<vlan_name>\S+)\s+(?P<mac>\S+)\s+"
        r"(?P<type>Learn|Static|S|D|L|P|DR)(?:,SE)?\s+"
        r".+?\s(?P<interfaces>\S+\.\d+)"
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        if not self.is_switch or not self.profile.command_exist(self, "ethernet-switching"):
            return []
        r = []
        vlans = {}
        for v in self.scripts.get_vlans():
            vlans[v["name"]] = v["vlan_id"]
        cmd = "show ethernet-switching table"
        if mac is not None:
            cmd += " | match %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for ll in self.cli(cmd).splitlines():
            match = self.rx_line.match(ll.strip())
            if match:
                if match.group("vlan_name") in vlans:
                    vlan_id = int(vlans[match.group("vlan_name")])
                else:
                    vlan_id = 1
                ifname = match.group("interfaces")
                if ifname.endswith(".0"):
                    ifname = ifname[:-2]
                r += [
                    {
                        "vlan_id": vlan_id,
                        "mac": match.group("mac"),
                        "interfaces": [ifname],
                        "type": {
                            "learn": "D",
                            "static": "S",
                            "d": "D",  # dynamic
                            "dr": "D",
                            "s": "S",  # static
                            "l": "D",  # locally learned
                            "p": "S",  # Persistent static
                            # "se": "s",  # statistics enabled - already in regexp
                            # "nm": "s",  # non configured MAC
                            # "r": "s",  # remote PE MAC
                            # "o": "s"  # ovsdb MAC
                        }[match.group("type").lower()],
                    }
                ]
        return r
