# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS_EE.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetMACAddressTable

rx_line = re.compile(r"^\S+\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+\d+\s+\d+\s+(?P<interfaces>\d+)\s+\d+\s+(?P<type>\d+)")


class Script(NOCScript):
    name = "Zyxel.ZyNOS_EE.get_mac_address_table"
    implements = [IGetMACAddressTable]

    def execute(self, interface=None):
        cmd = "sys sw mac list"
        if interface is not None:
            cmd += " port %s" % interface
        else:
            cmd += " all"
        macs = self.cli(cmd)
        r = []
        for l in macs.split("\n"):
            match = rx_line.match(l.strip())
            if match:
                r += [{
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"01":"D", "00":"S"}[match.group("type")],
                }]
        return r
