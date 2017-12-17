# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Qtech.QSW8200.get_mac_address_table
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
    name = "Qtech.QSW8200.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<mac>\S+\.\S+\.\S+)\s+(?P<iface>\S+)\s+(?P<vlan_id>\d+)\s+"
        r"(?P<type>\S+)",
        re.MULTILINE
    )

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address "
        if mac is not None:
            cmd += "%s" % mac
        else:
            cmd += "all"
        for match in self.rx_line.finditer(self.cli(cmd)):
            m = {
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("iface")],
                "type": {
                    "dynamic": "D",
                    "static": "S"
                }[match.group("type").lower()],
            }
            r += [m]
        return r
