# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_mac_address_table
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetMACAddressTable
from noc.lib.text import parse_table
import re


class Script(noc.sa.script.Script):
    name="HP.ProCurve.get_mac_address_table"
    implements=[IGetMACAddressTable]
    def execute(self,interface=None,vlan=None,mac=None):
        cmd="show mac-address"
        if vlan:
            vlans=[vlan]
        else:
            vlans=[r["vlan_id"] for r in self.scripts.get_vlans()]
        if mac:
            rmac=mac.replace(":","").lower()
        r=[]
        for v in vlans:
            for m,port in parse_table(self.cli("show mac-address vlan %d"%v)):
                rrmac=m.replace("-","").lower()
                if (not interface or port==interface) and (not mac or rmac==rrmac):
                    r+=[{
                        "vlan_id"    : v,
                        "mac"        : m,
                        "interfaces" : [port],
                        "type"       : "D"
                    }]
        return r
