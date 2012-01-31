# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "HP.ProCurve9xxx.get_mac_address_table"
    implements = [IGetMACAddressTable]

    ##
    ## Parse MAC address table
    ##
    dataline = re.compile(r"^[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4}")

    def parse_mac_table(self, s):
        r = []
        for line in s.splitlines():
            if self.dataline.match(line):
               l = line.split()
               r.append([l[0], l[1], l[3]])
        return r

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show mac-address"
        if vlan:
            vlans = [vlan]
        else:
            vlans = [r["vlan_id"] for r in self.scripts.get_vlans()]
        if mac:
            rmac = mac.replace(":", "").lower()
        r = []
        for v in vlans:
#            try:
                for m, port, type in self.parse_mac_table(self.cli("show mac-address vlan %d" % v)):
                    rrmac = m.replace(".", "").lower()
                    if (not interface or port == interface) \
                    and (not mac or rmac == rrmac):
                        r += [{
                            "vlan_id": v,
                            "mac": m,
                            "interfaces": [port],
                            "type": type
                        }]
#            except TypeError:
#                r = []
        return r
