# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Supertel.K2X.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Supertel.K2X.get_switchport"
    implements = [IGetSwitchport]

    rx_vlan = re.compile(
        r"(?P<vlan>\d+)\s+.+\s+(?P<rule>(Tagged|Untagged))\s+\S+",
        re.IGNORECASE)
    rx_description = re.compile(
        r"^(?P<interface>(g|t)\d+)\s+((?P<description>\S+)|)$",
        re.MULTILINE)
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

        # 802.1ad not supported!
        vlan_stack_status = {}

        # Try snmp first
        if self.has_snmp():
            try:
                # Get switchport index, name and description
                iface_name = {}
                iface_descr = {}
                interface_status = {}
                N = None
                for v in self.snmp.get_tables(["1.3.6.1.2.1.31.1.1.1.1",
                                               "1.3.6.1.2.1.31.1.1.1.18",
                                               "1.3.6.1.2.1.2.2.1.8"],
                                              bulk=True):
                    if v[1][:1] == 'g' or v[1][:2] == 'ch':
                        name = v[1]
                        iface_name.update({v[0]: name})
                        iface_descr.update({name: v[2]})
                        if name[:2] != 'ch':
                            interface_status.update({name: v[3]})

                # Make a list of tags for each interface or portchannel
                port_vlans = {}
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.4.2.1.3",
                                               "1.3.6.1.2.1.17.7.1.4.2.1.4",
                                               "1.3.6.1.2.1.17.7.1.4.2.1.5"],
                                              bulk=True):
                    tagged = v[2]
                    untagged = v[3]

                    s = self.hex_to_bin(untagged)
                    un = []
                    for i in iface_name:
                        j = int(i) - 1
                        if j < 1008:
                            iface = iface_name[i]
                            if iface not in port_vlans:
                                port_vlans.update({iface: {
                                    "tagged": [],
                                    "untagged": '',
                                    }})
                            if s[j] == '1':
                                port_vlans[iface]["untagged"] = v[1]
                                un += [j]

                    s = self.hex_to_bin(tagged)
                    for i in iface_name:
                        j = int(i) - 1
                        if j < 1008 and s[j] == '1' and j not in un:
                            iface = iface_name[i]
                            if iface not in port_vlans:
                                port_vlans.update({iface: {
                                    "tagged": [],
                                    "untagged": '',
                                    }})
                            port_vlans[iface]["tagged"].append(v[1])

                # Get switchport data and overall result
                r = []
                swp = {}
                write = False
                for name in interface_status:
                    if name in portchannel_members:
                        for p in portchannels:
                            if name in p["members"]:
                                name = p["interface"]
                                status = False
                                for interface in p["members"]:
                                    if interface_status.get(interface):
                                        status = True
                                description = iface_descr[name]
                                if not description:
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
                        description = iface_descr[name]
                        if not description:
                            description = ''
                        members = []
                        write = True
                    if write:
                        if name not in port_vlans:
                            tagged = []
                        else:
                            tagged = port_vlans[name]["tagged"]
                        swp = {
                            "status": status,
                            "description": description,
                            "802.1Q Enabled": len(port_vlans.get(name,
                                                                 '')) > 0,
                            "802.1ad Tunnel": vlan_stack_status.get(name,
                                                                    False),
                            "tagged": tagged,
                            }
                        if name in port_vlans:
                            if port_vlans[name]["untagged"]:
                                swp["untagged"] = port_vlans[name]["untagged"]
                        swp["interface"] = name
                        swp["members"] = members
                        r.append(swp)
                        write = False
                return r
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        # Make a list of tags for each interface or portchannel
        port_vlans = {}
        port_channels = portchannels
        for interface in interface_status:
            if interface in portchannel_members:
                for p in port_channels:
                    if interface in p["members"]:
                        interface = p["interface"]
                        port_channels.remove(p)
                        cmd = "show interfaces switchport port-channel %s" % interface[2:]
                        break
            else:
                cmd = "show interfaces switchport ethernet %s" % interface
            if interface not in port_vlans:
                port_vlans.update({interface: {
                    "tagged": [],
                    "untagged": '',
                    }
                })
            for vlan in self.rx_vlan.finditer(self.cli(cmd)):
                vlan_id = vlan.group("vlan")
                rule = vlan.group("rule")
                if rule == "Tagged":
                    port_vlans[interface]["tagged"].append(vlan_id)
                elif rule == "Untagged":
                    port_vlans[interface]["untagged"] = vlan_id

        # Get portchannels onse more!!!
        portchannels = self.scripts.get_portchannel()

        # Get switchport data and overall result
        r = []
        swp = {}
        write = False
        cmd = self.cli("show interfaces description")
        for match in self.rx_description.finditer(cmd):
            name = match.group("interface")

            if name in portchannel_members:
                for p in portchannels:
                    if name in p["members"]:
                        name = p["interface"]
                        status = False
                        for interface in p["members"]:
                            if interface_status.get(interface):
                                status = True
                        cmd = "show interfaces description port-channel %s" % name[2:]
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
                if interface_status[name]:
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
