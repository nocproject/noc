# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
from noc.sa.interfaces.base import MACAddressParameter


class Script(BaseScript):
    name = "Alstec.24xx.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_all = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<interface>\S+)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<type>\S+)\s*\n",
        re.MULTILINE)
    rx_iface = re.compile(
        r"^\s*(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>\S+)\s*\n",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-addr-table"
        rx_line = self.rx_all
        if interface is not None:
            """
            #show mac-addr-table interface 0/0
            ERROR: interface 0/0 not exist
            """
            if interface == "0/0":
                return []
            cmd += " interface %s" % interface
            rx_line = self.rx_iface
        r = []
        for match in rx_line.finditer(self.cli(cmd)):
            if match.group("type") == "Learned":
                mtype = "D"
            else:
                if match.group("type") == "Management":
                    mtype = "C"
                else:
                    mtype = "S"
            if interface is not None:
                _iface = interface
            else:
                _iface = match.group("interface")
            r.append({
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [_iface],
                "type": mtype
            })
        return r
