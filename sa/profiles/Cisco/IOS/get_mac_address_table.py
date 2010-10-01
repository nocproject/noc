# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
import re

rx_line=re.compile(r"^(?:\*\s+)?(?P<vlan_id>\d+)\s+(?P<mac>\S+)\s+(?P<type>\S+)\s+(?:\S+\s+){0,2}(?P<interfaces>.*)$")

class Script(noc.sa.script.Script):
    name="Cisco.IOS.get_mac_address_table"
    implements=[IGetMACAddressTable]
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac address-table"
        if mac is not None:
            cmd+=" address %s"%self.profile.convert_mac(mac)
        if interface is not None:
            cmd+=" interface %s"%interface
        if vlan is not None:
            cmd+=" vlan %s"%vlan
        try:
            macs=self.cli(cmd)
        except self.CLISyntaxError:
            cmd=cmd.replace("mac address-table","mac-address-table")
            macs=self.cli(cmd)
        r=[]
        for l in macs.splitlines():
            if l.startswith("Multicast Entries"):
                break # Additional section on 4500
            match=rx_line.match(l.strip())
            if match:
                mac=match.group("mac")
                if mac.startswith("3333."):
                    continue # Static entries
                interfaces=[i.strip() for i in match.group("interfaces").split(",")]
                interfaces=[i for i in interfaces if i.lower() not in ("router","switch","stby-switch","yes","no","-")]
                if not interfaces:
                    continue
                r.append({
                    "vlan_id"   : match.group("vlan_id"),
                    "mac"       : mac,
                    "interfaces": interfaces,
                    "type"      : {"dynamic":"D","static":"S"}[match.group("type").lower()],
                })
        return r
