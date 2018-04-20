# -*- coding: utf-8 -*-
<<<<<<< HEAD
# ---------------------------------------------------------------------
# Eltex.MES.get_switchport
# ---------------------------------------------------------------------
# Copyright (C) 2007-2015 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetswitchport import IGetSwitchport
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Eltex.MES.get_switchport"
    interface = IGetSwitchport

    TIMEOUT = 240

    rx_channel_description = re.compile(
        r"^(?P<interface>(p|P)o\d+)\s+(Up|Down)\s+(Not Present|Present)\s+((?P<description>\S+.+)|)$", re.MULTILINE)
=======
##----------------------------------------------------------------------
## Eltex.MES.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Eltex.MES.get_switchport"
    implements = [IGetSwitchport]

    rx_vlan = re.compile(
        r"^\s*(?P<vlan>\d+)\s+(?P<name>.+?)\s+(?P<rule>\S+)\s+(?P<type>\S+)\s*",
        re.IGNORECASE)
    rx_description = re.compile(
        r"^(?P<interface>(fa|gi|te)\S+)\s+((?P<description>\S+)|)$",
        re.MULTILINE)
    rx_channel_description = re.compile(
        r"^(?P<interface>Po\d+)\s+((?P<description>\S+)|)$", re.MULTILINE)
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
    rx_vlan_stack = re.compile(
        r"^(?P<interface>\S+)\s+(?P<role>\S+)\s*$", re.IGNORECASE)  # TODO

    def execute(self):

        # Get portchannels
        portchannels = self.scripts.get_portchannel()
        portchannel_members = []
        for p in portchannels:
            portchannel_members += p["members"]


        #TODO
        # Get 802.1ad status if supported
        vlan_stack_status = {}
#        try:
#            cmd = self.cli("show vlan-stacking")
#            for match in self.rx_vlan_stack.finditer(cmd):
#                if match.group("role").lower() == "tunnel":
#                    vlan_stack_status[int(match.group("interface"))] = True
#        except self.CLISyntaxError:
#            pass

        # Try snmp first
<<<<<<< HEAD
        if self.has_snmp():
=======
        if self.snmp and self.access_profile.snmp_ro:
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            try:
                # Get switchport index, name and description
                iface_name = {}
                iface_descr = {}
                interface_status = {}
                N = None
<<<<<<< HEAD
                for v in self.snmp.get_tables(["1.3.6.1.2.1.31.1.1.1.1",
                                               "1.3.6.1.2.1.31.1.1.1.18",
                                               "1.3.6.1.2.1.2.2.1.8"],
                                              bulk=True):
                    if v[1][:2] == 'fa' or v[1][:2] == 'gi' or v[1][:2] == 'te' or v[1][:2] == 'po':
                        name = v[1]
                        iface_name.update({v[0]: name})
                        iface_descr.update({name: v[2]})
                        if name[:2].lower() != 'po':
=======
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.31.1.1.1.18",
                    "1.3.6.1.2.1.2.2.1.8"], bulk=True):
                    if v[1][:2] == 'fa' or v[1][:2] == 'gi' or v[1][:2] == 'te' or v[1][:2] == 'po':
                        name = v[1]
                        name = name.replace('fa', 'Fa ')
                        name = name.replace('gi', 'Gi ')
                        name = name.replace('te', 'Te ')
                        name = name.replace('po', 'Po ')
                        iface_name.update({v[0]: name})
                        iface_descr.update({name: v[2]})
                        if name[:2] != 'Po':
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            interface_status.update({name: v[3]})

                # Make a list of tags for each interface or portchannel
                port_vlans = {}
<<<<<<< HEAD
                for v in self.snmp.get_tables(["1.3.6.1.2.1.17.7.1.4.3.1.2",
                                               "1.3.6.1.2.1.17.7.1.4.3.1.4"],
                                              bulk=True):
                    tagged = v[1]
                    untagged = v[2]
=======
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.7.1.4.3.1.1",
                    "1.3.6.1.2.1.17.7.1.4.3.1.2",
                    "1.3.6.1.2.1.17.7.1.4.3.1.4"], bulk=True):
                    tagged = v[2]
                    untagged = v[3]
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

                    s = self.hex_to_bin(untagged)
                    un = []
                    for i in iface_name:
                        j = int(i) - 1
                        if j < 1008:
                            iface = iface_name[i]
                            if iface not in port_vlans:
<<<<<<< HEAD
                                port_vlans.update({iface: {
                                    "tagged": [],
                                    "untagged": '1',
                                    }})
=======
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '1',
                                        }
                                    })
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            if s[j] == '1':
                                port_vlans[iface]["untagged"] = v[0]
                                un += [j]

                    s = self.hex_to_bin(tagged)
                    for i in iface_name:
                        j = int(i) - 1
                        if j < 1008 and s[j] == '1' and j not in un:
                            iface = iface_name[i]
                            if iface not in port_vlans:
<<<<<<< HEAD
                                port_vlans.update({iface: {
                                    "tagged": [],
                                    "untagged": '',
                                    }})
=======
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                            port_vlans[iface]["tagged"].append(v[0])

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
<<<<<<< HEAD
                            "status": status,
                            "description": description,
                            "802.1Q Enabled": len(port_vlans.get(name,
                                                                 '')) > 0,
                            "802.1ad Tunnel": vlan_stack_status.get(name,
                                                                    False),
                            "tagged": tagged,
                            }
=======
                                "status": status,
                                "description": description,
                                "802.1Q Enabled": len(port_vlans.get(name,
                                                '')) > 0,
                                "802.1ad Tunnel": vlan_stack_status.get(name,
                                                False),
                                "tagged": tagged,
                                }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
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
<<<<<<< HEAD
=======
        # Make a list of tags for each interface or portchannel
        r = []

>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Get interafces status
        interface_status = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

        port_vlans = {}
        port_channels = portchannels
        for interface in interface_status:
            if interface in portchannel_members:
                for p in port_channels:
                    if interface in p["members"]:
                        interface = p["interface"]
                        port_channels.remove(p)
                        break
            if interface not in port_vlans:
                port_vlans.update({interface: {
<<<<<<< HEAD
                    "tagged": [],
                    "untagged": '',
                    }
                })
            cmd = self.cli("show interfaces switchport %s" % interface)
            for vlan in parse_table(cmd, allow_wrap=True):
                vlan_id = vlan[0]
                rule = vlan[2]
                if rule == "Tagged":
                    port_vlans[interface]["tagged"].append(vlan_id)
                elif rule == "Untagged":
                    port_vlans[interface]["untagged"] = vlan_id
=======
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                })
            cmd = "show interfaces switchport %s" % interface
            for vlans in self.cli(cmd).splitlines():
                vlan = self.rx_vlan.match(vlans)
                if vlan:
                    vlan_id = vlan.group("vlan")
                    rule = vlan.group("rule")
                    if rule == "Tagged":
                        port_vlans[interface]["tagged"].append(vlan_id)
                    elif rule == "Untagged":  # and vlan_id != '1':
                        port_vlans[interface]["untagged"] = vlan_id
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce

        # Why portchannels=[] ???????
        # Get portchannels onse more!!!
        portchannels = self.scripts.get_portchannel()
<<<<<<< HEAD

=======
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
        # Get switchport data and overall result
        r = []
        swp = {}
        write = False
        cmd = self.cli("show interfaces description")
<<<<<<< HEAD
        for iface in parse_table(cmd, allow_wrap=True):
            name = iface[0]
=======
        for match in self.rx_description.finditer(cmd):
            name = match.group("interface")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
            name = name.replace('fa', 'Fa ')
            name = name.replace('gi', 'Gi ')
            name = name.replace('te', 'Te ')

            if name in portchannel_members:
                for p in portchannels:
                    if name in p["members"]:
                        name = p["interface"]
                        status = False
                        for interface in p["members"]:
                            if interface_status.get(interface):
                                status = True
                        cmd = "show interfaces description %s" % name
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
<<<<<<< HEAD
            elif name[:2].lower() in ['fa', 'gi', 'te']:
                if interface_status[name]:
                    status = True
                else:
                    status = False
                description = iface[3]
=======
            else:
                if interface_status.get(name):
                    status = True
                else:
                    status = False
                description = match.group("description")
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                if not description:
                    description = ''
                members = []
                write = True
            if write:
                swp = {
<<<<<<< HEAD
                    "status": status,
                    "description": description,
                    "802.1Q Enabled": len(port_vlans.get(name, None)) > 0,
                    "802.1ad Tunnel": vlan_stack_status.get(name, False),
                    "tagged": port_vlans[name]["tagged"],
                    }
=======
                        "status": status,
                        "description": description,
                        "802.1Q Enabled": len(port_vlans.get(name, None)) > 0,
                        "802.1ad Tunnel": vlan_stack_status.get(name, False),
                        "tagged": port_vlans[name]["tagged"],
                        }
>>>>>>> 2ab0ab7718bb7116da2c3953efd466757e11d9ce
                if port_vlans[name]["untagged"]:
                    swp["untagged"] = port_vlans[name]["untagged"]
                swp["interface"] = name
                swp["members"] = members
                r.append(swp)
                write = False
        return r
