# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line=re.compile(r"^\s*(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+(?P<interfaces>\S+\s+\S+).*$")

class Script(noc.sa.script.Script):
    name="Force10.FTOS.get_mac_address_table"
    implements=[IGetMACAddressTable]
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac-address-table"
        if mac is not None:
            cmd+=" address %s"%self.profile.convert_mac(mac)
        if interface is not None:
            cmd+=" interface %s"%interface
        if vlan is not None:
            cmd+=" vlan %s"%vlan
        vlans=self.cli(cmd+" | no-more")
        r=[]
        for l in vlans.split("\n"):
            match=rx_line.match(l.strip())
            if match:
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : match.group("mac"),
                    "interfaces": [match.group("interfaces")],
                    "type"      : {"Dynamic":"D"}[match.group("type")],
                })
        return r
