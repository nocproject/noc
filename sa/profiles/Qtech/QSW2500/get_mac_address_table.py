# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW2500.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Qtech.QSW2500.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(r"^(?P<mac>\S+)\s+(?P<iface>\d+)\s+(?P<vlan_id>\d+)\s*\S+", re.MULTILINE)

    def execute_cli(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address-table l2-address"
        if interface is not None:
            cmd += " port %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("iface")],
                    "type": "D",
                }
            ]
        return r
