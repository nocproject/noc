# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Dell.Powerconnect62xx.get_mac_address_table
# ---------------------------------------------------------------------
# Copyright (C) 2007-2011 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "Dell.Powerconnect62xx.get_mac_address_table"
    interface = IGetMACAddressTable
=======
##----------------------------------------------------------------------
## Dell.Powerconnect62xx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "Dell.Powerconnect62xx.get_mac_address_table"
    implements = [IGetMACAddressTable]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_line = re.compile(
        r"^(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<interface>\S+)\s+"
        r"(?P<type>\S+)\s*$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show bridge address-table"
        if interface is not None:
            cmd += " ethernet %s" % interface
        if vlan is not None:
            cmd += " vlan %d" % vlan
        r = []
        for match in self.rx_line.finditer(self.cli(cmd)):
            r_mac = match.group("mac")
            if (mac is not None) and (r_mac != mac):
                continue
            interface = match.group("interface")
            if interface == "cpu":
                continue
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": r_mac,
                "interfaces": [interface],
                "type": {
                    "dynamic":"D",
                    "static":"S"
                }[match.group("type").lower()]
            }]
        return r
