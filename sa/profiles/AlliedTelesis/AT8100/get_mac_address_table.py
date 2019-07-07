# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_mac_address_table
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
    name = "AlliedTelesis.AT8100.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<interfaces>\S+)\s+"
        r"(?P<mac>[\.0-9a-f]+)\s+\S+\s+(?P<type>\w+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None, vlan=None, mac=None):
        cmd = "show mac address-table"
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        r = []
        v = self.cli(cmd)
        for match in self.rx_line.finditer(v):
            if mac is not None and mac != match.group("mac"):
                continue
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {"dynamic": "D", "static": "S"}[match.group("type")],
                }
            ]
        return r
