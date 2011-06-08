# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
from __future__ import with_statement
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_switchport"
    implements = [IGetSwitchport]
    rx_portinfo = re.compile(r"Port No\s+:(?P<interface>\d+).\s*Active\s+:(?P<admin>\S+).\s*Name\s+:(?P<description>[A-Za-z0-9\-_/]*).\s*PVID\s+:(?P<untag>\d+)\s+Flow Control\s+:\S+$", re.MULTILINE | re.DOTALL)
    rx_vlan_stack = re.compile(r"^(?P<interface>\d+)\s+(?P<role>\S+).+$", re.MULTILINE)
    rx_vlan_tag = re.compile(r"^\s+(?P<port>\d+)\s+(?P<mode>(Untagged|Tagged))$", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        # Get portchannels
        portchannel_members = []
        portchannels = self.scripts.get_portchannel()
        for p in portchannels:
            portchannel_members += p["members"]
        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]
        # Get 802.1ad status if supported
        vlan_stack_status = {}
        try:
            for match in self.rx_vlan_stack.finditer(self.cli("show vlan-stacking")):
                if match.group("role").lower() == "tunnel":
                    vlan_stack_status[int(match.group("interface"))] = True
        except self.CLISyntaxError:
            pass
        # Get tagged ports in vlans
        vlan_ports = []
        with self.cached():
            for vlan in self.scripts.get_vlans():
                tagged_ports = []
                for match in self.rx_vlan_tag.finditer(self.cli("show vlan %d" % vlan["vlan_id"])):
                    if match.group("mode").lower() == "tagged":
                        tagged_ports += [match.group("port")]
                vlan_ports += [{
                    "vid": vlan["vlan_id"],
                    "ports": tagged_ports
                    }]
        # Make a list of tags for each port
        port_tags = {}
        for port in interface_status:
            tags = []
            for vlan in vlan_ports:
                if port in vlan["ports"]:
                    tags += [vlan["vid"]]
            port_tags[port] = tags
        # Get switchport data and overall result
        r = []
        for match in self.rx_portinfo.finditer(self.cli("show interface config *")):
            name = match.group("interface")
            if name not in portchannel_members:
                r += [{
                "interface": name,
                "status": interface_status.get(name, False),
                "description": match.group("description"),
                "802.1Q Enabled": len(port_tags.get(name, None)) > 0,
                "802.1ad Tunnel": vlan_stack_status.get(int(name), False),
                "untagged": int(match.group("untag")),
                "tagged": port_tags.get(name, None),
                "members": []
                }]
            else:
                for p in portchannels:
                    if name in p["members"]:
                        r += [{
                            "interface": p["interface"],
                            "status": interface_status.get(name, False),
                            "description": match.group("description"),
                            "802.1Q Enabled": True if len(port_tags.get(name, None)) > 0 else False,
                            "802.1ad Tunnel": vlan_stack_status.get(int(name), False),
                            "untagged": int(match.group("untag")),
                            "tagged": port_tags.get(name, None),
                            "members": p["members"]
                        }]
                    portchannels.remove(p)  # This works only if all parameters of all portchannels members are equal
                    break
        return r
