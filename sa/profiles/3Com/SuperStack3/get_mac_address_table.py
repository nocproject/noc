# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# 3Com.SuperStack3.get_mac_address_table
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable


class Script(BaseScript):
    name = "3Com.SuperStack3.get_mac_address_table"
    interface = IGetMACAddressTable

    rx_line = re.compile(
        r"Unit\s+(?P<unit>\d+)\s+Port\s+(?P<port>\d+)\s+"
        r"(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+(?P<type>Yes|No)\s*\n",
        re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        cmd = "bridge addressDatabase"
        if interface is not None:
            cmd += " summary %s" % interface
        else:
            cmd += " summary all"
        if mac is not None:
            cmd = " find %s" % self.profile.convert_mac(mac)
        macs = self.cli(cmd)
        for match in self.rx_line.finditer(self.cli(cmd)):
            vid = int(match.group("vlan_id"))
            if vlan is None or vid == vlan:
                interface = "%s:%s" % (match.group("unit"), match.group("port"))
                r += [{
                    "vlan_id": vid,
                    "mac": match.group("mac"),
                    "interfaces": [interface],
                    "type": {"no":"D", "yes":"S"}[match.group("type").lower()]
                }]
        return r
