# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>[:0-9A-F]+)\s+(?P<interfaces>\d+)\s+\S+\s+\S+\s+\S+\s+"
        r"\S+\s+(?P<vlan_id>[1-9][0-9]*)\s+(?P<type>.+)$"
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show switch fdb"
        if mac is not None:
            cmd += " address %s" % mac
        if interface is not None:
            cmd += " port(s) %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan

        r = []
        v = self.cli(cmd)
        for line in v.split("\n"):
            match = self.rx_line.match(line.strip())
            if match:
                vlan_id = int(match.group("vlan_id"))
                r += [
                    {
                        "vlan_id": vlan_id,
                        "mac": match.group("mac"),
                        "interfaces": [match.group("interfaces")],
                        "type": {
                            "Dynamic": "D",
                            "Static": "S",
                            "Static (fixed,non-aging)": "S",
                            "Multicast": "M",
                        }[match.group("type")],
                    }
                ]
        return r
