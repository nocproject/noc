# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
##
## Cisco.IOS.get_vlans
##
class Script(NOCScript):
    name="Cisco.IOS.get_vlans"
    implements=[IGetVlans]
    
    ##
    ## Extract vlan information
    ##
    rx_vlan_line=re.compile(r"^(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s", re.MULTILINE)
    def extract_vlans(self, data):
        r=[]
        for match in self.rx_vlan_line.finditer(data):
            name=match.group("name")
            vlan_id=int(match.group("vlan_id"))
            if vlan_id>=1000 and vlan_id<=1005\
                    and name in ["fddi-default","trcrf-default","token-ring-default","fddinet-default","trbrf-default","trnet-default"]:
                continue
            r+=[{"vlan_id": vlan_id, "name": name}]
        return r
        
    
    ##
    ## Cisco uBR7100, uBR7200, uBR7200VXR, uBR10000 Series
    ##
    rx_vlan_ubr=re.compile(r"^(\S+\s+){4}(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)", re.MULTILINE)
    @NOCScript.match(version__contains="BC")
    def execute_ubr(self):
        vlans=self.cli("show running-config | include cable dot1q-vc-map")
        r=[]
        for match in self.rx_vlan_ubr.finditer(vlans):
            r+=[{"vlan_id": int(match.group("vlan_id")), "name": match.group("name")}]
        return r
    
    ##
    ## 18xx/28xx/38xx/72xx with EtherSwitch module
    ##
    @NOCScript.match(platform__regex=r"([123]8[0-9]{2}|72[0-9]{2})")
    def execute_vlan_switch(self):
        vlans=self.cli("show vlan-switch")
        vlans, _=vlans.split("\nVLAN Type", 1)
        return self.extract_vlans(vlans)
    
    ##
    ## Other
    ##
    @NOCScript.match()
    def execute_vlan_brief(self):
        vlans=self.cli("show vlan brief")
        return self.extract_vlans(vlans)
    
