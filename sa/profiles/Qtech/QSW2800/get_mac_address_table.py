# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Qtech.QSW2800.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+\S+\s+"
        r"(?P<iface>\S+)", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += "address %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for match in self.rx_line.finditer(self.cli(cmd)):
            iface = match.group("iface")
            m = {
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [iface],
                "type": {
                    "dynamic": "D",
                    "static": "S",
                    "permanent": "S",
                    "self": "S",
                    "secured": "S"
                }[match.group("type").lower()],
            }
            if iface == 'CPU':
                m["type"] = "C"
            r += [m]
        return r
