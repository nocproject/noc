# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport
import re
 
 
class Script(NOCScript):
    name = "Alcatel.AOS.get_switchport"
    implements = [IGetSwitchport]
    rx_line = re.compile(r"\n\s+(?P<interface>\S+)\s+(?P<status>\S+)\s+(10000|1000|-)\s+", re.MULTILINE)
    rx_line_vlan = re.compile(r"^\s+(?P<vlan>\d+)\s+(?P<interface>\S+)\s+(?P<vlan_type>\S+)\s+(?P<status>\S+)$", re.MULTILINE)
 
    def execute(self):
        r = []
        members = []
 
        iface_vlans = {}
        for match in self.rx_line_vlan.finditer(self.cli("show vlan port")):
            interface = match.group("interface")
            if interface not in iface_vlans:
                iface_vlans[interface] = {
                                   "tagged": [],
                                   "untagged": [],
                                   }
            vlan_type = match.group("vlan_type")
            if vlan_type == "default":
                iface_vlans[interface]["untagged"].append(match.group("vlan"))
            if vlan_type == "qtagged":
                iface_vlans[interface]["tagged"].append(match.group("vlan"))
 
        for match in self.rx_line.finditer(self.cli("show interfaces status")):
            interface = match.group("interface")
            r += [{
                "interface": interface,
                "status": match.group("status") == "enabled",
                "description"    : "",
                "802.1Q Enabled": "True",
                "802.1ad Tunnel": False,
                "untagged": iface_vlans[interface]["untagged"][0],
                "tagged": iface_vlans[interface]["tagged"],
                "members": members,
                }]
        return r
