# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## AlliedTelesis.AT9900.get_mac_address_table
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
    name = "AlliedTelesis.AT9900.get_mac_address_table"
    implements = [IGetMACAddressTable]
    rx_line = re.compile(r"^\s*(?P<vlan_id>\d+)\s*(?P<mac>\S+)\s*(?P<interfaces>\S+)\s*(?P<type>\S+)\s*(?P<test>\d+)", re.IGNORECASE)

    def execute(self, interface=None, vlan=None, mac=None):
        cmd = "show switch fdb"
        if mac is not None:
            cmd += " address=%s" % mac
        if interface is not None:
            cmd += " port=%s" % interface
        if vlan is not None:
            cmd += " vlan=%s" % vlan
        vlans = self.cli(cmd)
        vlans = self.strip_first_lines(vlans, 6)
        r = []
        for l in vlans.split("\n"):
            match = self.rx_line.match(l.strip())
            if match:
                r += [{
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : [match.group("type")],
                }]
        return r
