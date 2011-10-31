# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9400.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable


class Script(NOCScript):
    name = "AlliedTelesis.AT9400.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>[:0-9a-fA-F]+)\s+(?P<interfaces>\d+)\s+(?P<type>[\(\)\,\-\w\s]+)$")

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show switch fdb"
        if mac is not None:
            cmd += " address=%s" % mac
        if interface is not None:
            cmd += " port(s)=%s" % interface
        if vlan is not None:
            cmd += " vlan=%s" % vlan
        vlans = self.cli(cmd)
        vlans = self.strip_first_lines(vlans, 4)
        r = []
        for l in vlans.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r += [{
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"Dynamic":"D", "Static":"S",
                                   "Static (fixed,non-aging)":"S",
                                   "Multicast":"M"}[match.group("type")],
                }]
        return r
