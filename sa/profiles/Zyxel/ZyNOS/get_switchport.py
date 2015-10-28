# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport


class Script(BaseScript):
    name = "Zyxel.ZyNOS.get_switchport"
    interface = IGetSwitchport

    rx_portinfo = re.compile(
            r"Port No\s+:(?P<interface>\d+)\n"
            r"\s*Active\s+:(?P<admin>\S+)\n"
            r"\s*Name\s+:(?P<description>.+)?\n"
            r"\s*PVID\s+:(?P<untag>\d+)\s+Flow Control\s+:\S+$",
            re.MULTILINE)
    rx_vlan_stack = re.compile(
            r"^(?P<interface>\d+)\s+(?P<role>\S+).+$",
            re.MULTILINE)
    rx_vlan_stack_global = re.compile(r"^Operation:\s+(?P<status>active)$")
    rx_vlan_ports = re.compile(
            r"\s+\d+\s+(?P<vid>\d+)\s+\S+\s+\S+\s+"
            r"Untagged\s+:(?P<untagged>[0-9,\-]*)."
            r"\s+Tagged\s+:(?P<tagged>[0-9,\-]*)",
            re.MULTILINE | re.DOTALL)

    def execute(self):
        # Get portchannels
        portchannel_members = []
        portchannels = self.scripts.get_portchannel()
        for p in portchannels:
            portchannel_members += p["members"]

        # Get interafces' status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        # Get 802.1ad status if supported
        vlan_stack_status = {}
        try:
            cmd = self.cli("show vlan-stacking")
            match = self.rx_vlan_stack_global.match(cmd)
            if match:
                for match in self.rx_vlan_stack.finditer(cmd):
                    if match.group("role").lower() == "tunnel":
                        vlan_stack_status[int(match.group("interface"))] = True
        except self.CLISyntaxError:
            pass

        # Get ports in vlans
        vlan_ports = []
        for match in self.rx_vlan_ports.finditer(self.cli("show vlan")):
            vlan_ports += [{
                "vid": match.group("vid"),
                "tagged": self.expand_rangelist(match.group("tagged")),
                "untagged": self.expand_rangelist(match.group("untagged")),
            }]

        # Make a list of tags for each port
        port_tags = {}
        for port in interface_status:
            tags = []
            untag = []
            for vlan in vlan_ports:
                if int(port) in vlan["tagged"]:
                    tags += [vlan["vid"]]
                elif int(port) in vlan["untagged"]:
                    untag = vlan["vid"]
            port_tags[port] = {"tags": tags, "untag": untag}

        # Get switchport data and overall result
        r = []
        swp = {}
        for match in self.rx_portinfo.finditer(
            self.cli("show interface config *")):
            name = match.group("interface")
            swp = {
                "status": interface_status.get(name, False),
                "802.1Q Enabled": len(port_tags[name].get("tags", None)) > 0,
                "802.1ad Tunnel": vlan_stack_status.get(int(name), False),
                "tagged": port_tags[name]["tags"],
            }
            if match.group("description"):
                swp["description"] = match.group("description")
            if port_tags[name]["untag"]:
                swp["untagged"] = port_tags[name]["untag"]
            if name not in portchannel_members:
                swp["interface"] = name
                swp["members"] = []
                r += [swp]
            else:
                for p in portchannels:
                    if name in p["members"]:
                        swp["interface"] = p["interface"]
                        swp["members"] = p["members"]
                        r += [swp]
                        st = False
                        for m in p["members"]:
                            st = interface_status.get(name, False)
                            if st:
                                break
                        swp["status"] = st
                        portchannels.remove(p)
                        break

        return r
