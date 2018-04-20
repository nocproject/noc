# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ----------------------------------------------------------------------
# Alcatel.AOS.get_switchport
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport

 
class Script(BaseScript):
    name = "Alcatel.AOS.get_switchport"
    interface = IGetSwitchport
=======
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
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
            if i:
                cli_ag = self.cli("show vlan port %s" % i)
                tagget = []
                untagged = []
=======
            member = pc["members"]
            if i:
                cli_ag = self.cli("show vlan port %s" % i)
                tagget = []
                untagget = []
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                for match_ag in self.rx_line_vlan_ag.finditer(cli_ag):
                     vlan = match_ag.group("vlan")
                     vlan_type = match_ag.group("vlan_type")
                     if vlan_type == "default":
<<<<<<< HEAD
                        untagged = vlan
=======
                        untagget = vlan
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                       "untagged": untagged,
=======
                       "untagged": untagget,
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
                    "tagged": []
                }
            vlan_type = match.group("vlan_type")
            if vlan_type == "default":
                iface_vlans[interface]["untagged"] = match.group("vlan")
            if vlan_type == "qtagged":
                iface_vlans[interface]["tagged"] += [match.group("vlan")]
=======
                    "tagged": [],
                    "untagged": [],
                }
            vlan_type = match.group("vlan_type")
            if vlan_type == "default":
                iface_vlans[interface]["untagged"].append(match.group("vlan"))
            if vlan_type == "qtagged":
                iface_vlans[interface]["tagged"].append(match.group("vlan"))
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
 
        for match in self.rx_line.finditer(self.cli("show interfaces status")):
            interface = match.group("interface")
            if interface not in portchannel_members:
<<<<<<< HEAD
                i = {
=======
                r += [{
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                    "interface": interface,
                    "status": match.group("status") == "enabled",
                    "description": "",
                    "802.1Q Enabled": "True",
                    "802.1ad Tunnel": False,
<<<<<<< HEAD
                    "tagged": iface_vlans[interface]["tagged"] if interface in iface_vlans else [],
                    "members": members,
                }
                if interface in iface_vlans and "untagged" in iface_vlans[interface]:
                    i["untagged"] = iface_vlans[interface]["untagged"]
                r += [i]
=======
                    "untagged": iface_vlans[interface]["untagged"][0],
                    "tagged": iface_vlans[interface]["tagged"],
                    "members": members,
                }]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        return r
