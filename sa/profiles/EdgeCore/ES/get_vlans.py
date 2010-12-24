# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## EdgeCore.ES.get_vlans
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC Modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetVlans
##
## EdgeCore.ES.get_vlans
##
class Script(NOCScript):
    name="EdgeCore.ES.get_vlans"
    cache=True
    implements=[IGetVlans]
    ##
    ## ES4626 = Cisco Style
    ##
    rx_vlan_line_4626=re.compile(r"^\s*(?P<vlan_id>\d{1,4})\s+(?P<name>\S+)\s+", re.IGNORECASE|re.MULTILINE)
    @NOCScript.match(platform__contains="4626")
    def execute_4626(self):
        vlans=self.cli("show vlan")
        return [{"vlan_id": int(match.group("vlan_id")) ,"name": match.group("name")} for match in self.rx_vlan_line_4626.finditer(vlans)]
    
    ##
    ## ES4612 or 3526S
    ##
    rx_vlan_line_4612=re.compile(r"^\s*(?P<vlan_id>\d{1,4})\s+\S+\s+(?P<name>\S+)\s+", re.IGNORECASE|re.MULTILINE)
    @NOCScript.match(platform__contains="4612")
    @NOCScript.match(platform__contains="3526S")
    def execute_4612(self):
        vlans=self.cli("show vlan")
        return [{"vlan_id": int(match.group("vlan_id")) ,"name": match.group("name")} for match in self.rx_vlan_line_4612.finditer(vlans)]

    ##
    ## Other
    ##
    rx_vlan_line_3526=re.compile(r"^VLAN ID\s*?:\s+?(?P<vlan_id>\d{1,4})\n.*?Name\s*?:\s+(?P<name>\S*?)\n", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    @NOCScript.match()
    def execute_3526(self):
        vlans=self.cli("show vlan")
        return [{"vlan_id": int(match.group("vlan_id")), "name": match.group("name")} for match in self.rx_vlan_line_3526.finditer(vlans)]
    
