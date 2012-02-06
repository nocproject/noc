# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable, IGetVlans
import re

rx_line = re.compile(r"(?P<vlan_name>[^ ]+)\s+(?P<mac>[^ ]+)\s+(?P<type>Learn|Static)\s+[^ ]+\s+(?P<interfaces>.*)$", re.IGNORECASE)


class Script(noc.sa.script.Script):
    name = "Juniper.JUNOS.get_mac_address_table"
    implements = [IGetMACAddressTable]
    requires = [("get_vlans", IGetVlans)]

    def execute(self, interface=None, vlan=None, mac=None):
        r = []
        vlans = {}
        for v in self.scripts.get_vlans():
            vlans[v["name"]] = v["vlan_id"]
        cmd = "show ethernet-switching table"
        if mac is not None:
            cmd += " | match %s" % mac
        if interface is not None:
            cmd += " interface %s" % interface
        if vlan is not None:
            cmd += " vlan %s" % vlan
        for l in self.cli(cmd).splitlines():
            match = rx_line.match(l.strip())
            if match:
                vlan_id = int(vlans[match.group("vlan_name")])
                r += [{
                    "vlan_id": vlan_id,
                    "mac": match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type": {
                        "learn":"D",
                         "static":"S"
                    }[match.group("type").lower()],
                }]
        return r
