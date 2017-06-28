# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTP.get_mac_address_table
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
    name = "Eltex.LTP.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_gpon = re.compile(
        r"^\s*\d+\s+\S+\s+\d+\s+(?P<interfaces>\d+)\s+\d+\s+"
        r"(?P<vlan_id>\d+)\s+(\d+\s+)?\s+\d+\s+(?P<mac>\S+:\S+)\s*\n",
        re.MULTILINE)

    rx_switch = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interfaces>(\S+ \d+|\S+))\s+"
        r"(?P<type>\S+)\s+\S+\s+\S+\s+\d+\s*$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        # GPON ports
        cmd = "show mac interface gpon-port "
        if interface is not None:
            cmd += " %s" % interface
        else:
            cmd += " 0-7"
        for match in self.rx_gpon.finditer(self.cli(cmd)):
            interfaces = match.group("interfaces")
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [interfaces],
                "type": "D"
            }]
        # 
        #cmd = "show mac interface ont "
        return r
