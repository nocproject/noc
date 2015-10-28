# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Cisco_CLI.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetmacaddresstable import IGetMACAddressTable
import re


class Script(BaseScript):
    name = "DLink.DxS_Cisco_CLI.get_mac_address_table"
    interface = IGetMACAddressTable
    rx_line = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+"
        r"(?P<interfaces>\S+\s*\d+\/\d+)$", re.MULTILINE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address-table"
        if mac is not None:
            cmd += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        try:
            macs = self.cli(cmd)
        except self.CLISyntaxError:
            # Not supported at all
            raise self.NotSupportedError()
        r = []
        for match in self.rx_line.finditer(macs):
            r += [{
                "vlan_id": match.group("vlan_id"),
                "mac": match.group("mac"),
                "interfaces": [match.group("interfaces")],
                "type": {
                    "dynamic":"D",
                     "static":"S"
                }[match.group("type").lower()]
            }]
        return r
