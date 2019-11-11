# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_mac_address_table
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
    name = "Zhone.Bitstorm.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"^(?:(?P<slot>\d+)\s+)?(?P<interfaces>\S+|(?:\d+:\d+|eth\d+))\s+(?:(?:\d+/\d+|N/A)\s+)?(?P<mac>[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2}-"
        r"[0-9a-f]{2}-[0-9a-f]{2}-[0-9a-f]{2})\s+(?P<type>\S+)\s+(?P<vlan_id>\d+)",
        re.MULTILINE,
    )

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge"
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            ifname = match.group("interfaces")
            if match.group("slot") and not ifname.startswith("eth"):
                ifname = "%s/%s" % (match.group("slot"), ifname)
            if interface and interface != ifname:
                continue
            ifname = ifname.replace(":", "/")
            mac1 = match.group("mac")
            if mac and mac != mac1:
                continue
            vlan_id = match.group("vlan_id")
            if vlan and vlan != vlan_id:
                continue
            r += [
                {
                    "vlan_id": vlan_id,
                    "mac": mac1,
                    "interfaces": [ifname],
                    "type": {"learned": "D", "static": "S", "self": "C"}[match.group("type")],
                }
            ]
        return r
