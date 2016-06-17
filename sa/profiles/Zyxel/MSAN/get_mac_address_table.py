# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.MSAN.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "Zyxel.MSAN.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+"
        r"(?P<interface>.+)\s*$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac"
        if mac is not None:
            cmd += " %s" % mac
        if (interface is not None) and (interface.startswith("enet")):
            cmd += " %s" % interface
        if vlan is not None:
            cmd += " vid %s" % vlan
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            return []
        r = []
        for match in self.rx_line.finditer(macs):
            mac_address = match.group("mac")
            r.append({
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interface").replace(" ", "")],
                "type": "D"
            })
        return r
