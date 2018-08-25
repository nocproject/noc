# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "SKS.SKS.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line1 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+"
        r"(?P<iface>\S+)", re.MULTILINE)
    rx_line2 = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<iface>\S+)\s+"
        r"(?P<type>\S+)", re.MULTILINE)
    rx_status = re.compile("Vlan\s+Mac Address\s+Type\s+Ports", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac address-table"
        if mac is not None:
            cmd += "address %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        c = self.cli(cmd)
        if bool(self.rx_status.search(c)):
            rx_line = self.rx_line1
        else:
            rx_line = self.rx_line2
        for match in rx_line.finditer(c):
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("iface")],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "self": "C",
                    "secure": "S"
                }[match.group("type").lower()],
            }]
        return r
