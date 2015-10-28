# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Alcatel.AOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
import re
 
 
class Script(BaseScript):
    name = "Alcatel.AOS.get_switchport"
    interface = IGetSwitchport
    rx_line = re.compile(r"\n\s+(?P<interface>\S+)\s+(?P<status>\S+)\s+(10000|1000|-)\s+",
                         re.MULTILINE)
    rx_line_vlan = re.compile(r"^\s+(?P<vlan>\d+)\s+(?P<interface>\S+)\s+(?P<vlan_type>\S+)\s+(?P<status>\S+)$",
                              re.MULTILINE)
    rx_line_vlan_ag = re.compile(r"^\s+(?P<vlan>\S+)\s+(?P<vlan_type>\S+)\s+(forwarding|inactive)$",
                                 re.MULTILINE)
    def execute(self):
        r = []
        members = []
 
        iface_vlans = {}
        portchannel_members = {}
        for pc in self.scripts.get_portchannel():
            members = []
            i = pc["interface"]
            member = pc["members"]
            if i:
                cli_ag = self.cli("show vlan port %s" % i)
                tagget = []
                untagget = []
                for match_ag in self.rx_line_vlan_ag.finditer(cli_ag):
                     vlan = match_ag.group("vlan")
                     vlan_type = match_ag.group("vlan_type")
                     if vlan_type == "default":
                        untagget = vlan
                     if vlan_type == "qtagged":
                         tagget += [vlan]
                shortname = self.profile.convert_interface_name(i)
                for p in self.scripts.get_portchannel():
                    if p["interface"] == shortname:
                        members = p["members"]
                r += [{"interface": "Ag %s" % i,
                       "status": "enabled",
                       "description": "",
                       "802.1Q Enabled": "True",
                       "802.1ad Tunnel": False,
                       "untagged": untagget,
                       "tagged": tagget,
                       "members": members,
                    }]
        if members:
            for m in pc["members"]:
                portchannel_members[m] = (i)

        for match in self.rx_line_vlan.finditer(self.cli("show vlan port")):
            members = []
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
            if interface not in portchannel_members:
                r += [{
                    "interface": interface,
                    "status": match.group("status") == "enabled",
                    "description": "",
                    "802.1Q Enabled": "True",
                    "802.1ad Tunnel": False,
                    "untagged": iface_vlans[interface]["untagged"][0],
                    "tagged": iface_vlans[interface]["tagged"],
                    "members": members,
                }]
        return r
