# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## NSN.hiX56xx.get_mac_address_table
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "NSN.hiX56xx.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile("^(?P<interfaces>\d+/\d+(?:/\d+)?)\s+(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(\S+)\s+(?P<type>\S+)\s+", re.MULTILINE)
    TIMEOUT = 600

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac"
        reset = ""
        if mac is not None:
            reset += " address %s" % self.profile.convert_mac(mac)
        if interface is not None:
            reset += " port %s" % interface
        if vlan is not None:
            reset += " vlan %s" % vlan
        if not reset:
            reset = " port 1/1/1-10/72/4"
        cmd = cmd + reset
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
                    "dynamic": "D", "static": "S", "p-locked": "S"
                }[match.group("type").lower()]
            }]
        return r
