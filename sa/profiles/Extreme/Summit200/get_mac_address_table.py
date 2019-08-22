# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Extreme.Summit200.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\d\S+\s+(?P<mac>\S+)\s+\S+\((?P<vlan_id>\d+)\)\s+\d+\s+\d+\s+"
        r"(?P<type>([dhmis\s]+))\s+(?P<interfaces>\d+)",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show fdb"
        if mac is not None:
            cmd += " %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " ports %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        r = []
        v = self.cli(cmd)
        for match in self.rx_line.finditer(v):
            mactype = match.group("type")
            r += [
                {
                    "vlan_id": match.group("vlan_id"),
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "d m": "D",
                        "dhm": "D",
                        "dhmi": "D",
                        "d mi": "D",
                        "s m": "S",
                        "shm": "S",
                    }[mactype.strip()],
                }
            ]
        return r
