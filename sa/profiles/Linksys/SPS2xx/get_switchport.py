# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Linksys.SPS2xx.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Linksys.SPS2xx.get_switchport"
    implements = [IGetSwitchport]

    rx_vlan = re.compile(
        r"^\s*(?P<vlan>\d+)\s+(?P<name>.+?)\s+(?P<rule>\S+)\s+(?P<type>\S+)\s*",
        re.IGNORECASE)
    rx_description = re.compile(
        r"^(?P<interface>(e|g|t)\S+)\s+((?P<description>\S+)|)$", re.MULTILINE)
    rx_channel_description = re.compile(
        r"^(?P<interface>ch\d+)\s+((?P<description>\S+)|)$", re.MULTILINE)
    rx_vlan_stack = re.compile(
        r"^(?P<interface>\S+)\s+(?P<role>\S+)\s*$", re.IGNORECASE)  # TODO

    def execute(self):
        # Get portchannels
        portchannels = self.scripts.get_portchannel()
        portchannel_members = []
        for p in portchannels:
            portchannel_members += p["members"]

        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        #TODO
        # Get 802.1ad status if supported
        vlan_stack_status = {}
        try:
            stack = self.cli("show vlan-stacking")
            for match in self.rx_vlan_stack.finditer(stack):
                if match.group("role").lower() == "tunnel":
                    vlan_stack_status[int(match.group("interface"))] = True
        except self.CLISyntaxError:
            pass

        # Make a list of tags for each interface or portchannel
        port_vlans = {}
        port_channels = portchannels
        for interface in interface_status:
            if interface in portchannel_members:
                for p in port_channels:
                    if interface in p["members"]:
                        interface = p["interface"]
                        vlan_list = self.cli(
                            "show interfaces switchport port-channel %s"
                            % interface).splitlines()
                        port_channels.remove(p)
                        break
            else:
                cmd = "show interfaces switchport ethernet %s" % interface
                vlan_list = self.cli(cmd).splitlines()
            if interface not in port_vlans:
                port_vlans.update({interface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                })
            for vlans in vlan_list:
                vlan = self.rx_vlan.match(vlans)
                if vlan:
                    vlan_id = vlan.group("vlan")
                    rule = vlan.group("rule")
                    if rule == "Tagged":
                        port_vlans[interface]["tagged"].append(vlan_id)
                    elif rule == "Untagged" and vlan_id != '1':
                        port_vlans[interface]["untagged"] = vlan_id

        # Why portchannels=[] ???????
        # Get portchannels onse more!!!
        portchannels = self.scripts.get_portchannel()
        # Get switchport data and overall result
        r = []
        swp = {}
        write = False
        int_desc = self.cli("show interfaces description")
        for match in self.rx_description.finditer(int_desc):
            name = match.group("interface")
            if name in portchannel_members:
                for p in portchannels:
                    if name in p["members"]:
                        name = p["interface"]
                        status = False
                        for interface in p["members"]:
                            if interface_status.get(interface):
                                status = True
                        cmd = "show interfaces description port-channel %s" % name
                        desc = self.cli(cmd)
                        match = self.rx_channel_description.search(desc)
                        if match:
                            description = match.group("description")
                            if not description:
                                description = ''
                        else:
                            description = ''
                        members = p["members"]
                        portchannels.remove(p)
                        write = True
                        break
            else:
                if interface_status.get(name):
                    status = True
                else:
                    status = False
                description = match.group("description")
                if not description:
                    description = ''
                members = []
                write = True
            if write:
                swp = {
                        "status": status,
                        "description": description,
                        "802.1Q Enabled": len(port_vlans.get(name, None)) > 0,
                        "802.1ad Tunnel": vlan_stack_status.get(name, False),
                        "tagged": port_vlans[name]["tagged"],
                        }
                if port_vlans[name]["untagged"]:
                    swp["untagged"] = port_vlans[name]["untagged"]
                swp["interface"] = name
                swp["members"] = members
                r.append(swp)
                write = False
        return r
