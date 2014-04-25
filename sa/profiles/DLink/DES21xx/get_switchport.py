# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "DLink.DES21xx.get_switchport"
    implements = [IGetSwitchport]
    rx_vlan_ports = re.compile(
        r"VLAN_ID:(?P<vid>\d+).+?TAG PORT:(?P<tagged>[0-9 ]*).+?"
        r"UNTAG PORT:(?P<untagged>[0-9 ]*)\s*", re.MULTILINE | re.DOTALL)

    def execute(self):
        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        # Get ports in vlans
        vlan_ports = []
        for match in self.rx_vlan_ports.finditer(self.cli("show vlan", cached=True)):
            vlan_ports += [{
                "vid": match.group("vid"),
                "tagged": self.expand_rangelist(match.group("tagged").replace(" ", ",")),
                "untagged": self.expand_rangelist(match.group("untagged").replace(" ", ",")),
            }]

        # Make a list of tags for each port
        port_tags = {}
        for port in interface_status:
            tags = []
            untag = 1
            for vlan in vlan_ports:
                if int(port) in vlan["tagged"]:
                    tags += [vlan["vid"]]
                elif int(port) in vlan["untagged"]:
                    untag = vlan["vid"]
            port_tags[port] = {"tags": tags, "untag": untag}

        # Get switchport data and overall result
        r = []
        d = {}
        for name in interface_status.keys():
            d = {
                     "interface": name,
                        "status": interface_status.get(name, False),
                "802.1Q Enabled": len(port_tags[name].get("tags", None)) > 0,
                "802.1ad Tunnel": False,
                       "members": [],
                        "tagged": port_tags[name]["tags"]
            }
            if port_tags[name]["untag"]:
                d["untagged"] = port_tags[name]["untag"]
            r += [d]

        return r
