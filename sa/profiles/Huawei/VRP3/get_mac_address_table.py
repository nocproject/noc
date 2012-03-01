# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_mac_address_table
## sergey.sadovnikov@gmail.com
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from __future__ import with_statement
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
import re


class Script(NOCScript):
    name = "Huawei.VRP3.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"^\s*(?:\d+)\s+(?:\d+)\s+(?:\d+)\s+(?P<vlan_id>\d+)\s+(?P<interfaces>\d+/\d+)\s+(?P<mac>\S+)", re.MULTILINE)
    TIMEOUT = 600

    def execute(self, interface=None, vlan=None, mac=None):
        with self.configure():
            self.cli("interface lan 0/0")
            cmd = "show mac-table"
            reset = ""
            if mac is not None:
                reset += " address %s" % self.profile.convert_mac(mac)
            if interface is not None:
                reset += " port %s" % interface
            if vlan is not None:
                reset += " vlan %s" % vlan
            if not reset:
                reset = " all"
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
                    "type": "D"
                }]
            return r
