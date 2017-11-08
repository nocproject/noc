# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_mac_address_table
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
    name = "Alstec.MSPU.get_mac_address_table"
    interface = IGetMACAddressTable
    cache = True

    rx_line = re.compile(
        r"^\s*(?P<port_no>\d+)\s+(?P<mac>\S+)\s+(?P<cpu>yes|no)\s+\d+\.\d+",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        v = self.scripts.get_arp()
        for i in v:
            if interface is None:
                iface = i["interface"]
            else:
                iface = interface
            break
        cmd = "context ip router brctl showmacs %s" % iface
        for match in self.rx_line.finditer(self.cli(cmd, cached=True)):
            r += [{
                "vlan_id": 1,
                "mac": match.group("mac"),
                "interfaces": [match.group("port_no")],
                "type": {
                    "no": "D",
                    "yes": "C"
                }[match.group("cpu").lower()],
            }]
        return r
