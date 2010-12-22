# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP.get_vlans
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

class Script(NOCScript):
    name="Huawei.VRP.get_vlans"
    implements=[IGetVlans]

    rx_vlan_line_vrp5=re.compile(r"^(?P<vlan_id>\d{1,4})\s*?.*?", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    @NOCScript.match(version__startswith="5.")
    def execute_vrp5(self):
        vlans=self.cli("display vlan")
        return [{"vlan_id": int(match.group("vlan_id")), "name": "VLAN" + match.group("vlan_id")} for match in self.rx_vlan_line_vrp5.finditer(vlans)]

    rx_vlan_line_vrp3=re.compile(r"^\sVLAN ID:\s+?(?P<vlan_id>\d{1,4})\n.*?Name:\s+(?P<name>.*?)\n.*?(\n\n|$)", re.IGNORECASE|re.DOTALL|re.MULTILINE)
    @NOCScript.match()
    def execute_vrp3(self):
        vlans=self.cli("display vlan all")
        return [{"vlan_id": int(match.group("vlan_id")), "name": match.group("name")} for match in self.rx_vlan_line_vrp3.finditer(vlans)]

    
