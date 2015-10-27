# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1910.get_switchport
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
    name = "HP.1910.get_switchport"
    implements = [IGetSwitchport]

    rx_iface = re.compile(
        r"^\s*(?P<iface>\S+Ethernet\S+) current state:\s+(?P<status>(UP|DOWN|Administratively DOWN))\s*$",
        re.IGNORECASE)
    rx_description = re.compile(
        r"^\s*Description:\s+(?P<description>.+)$",
        re.MULTILINE)
    rx_type = re.compile(r"^\s*Port link-type: (?P<type>\S+)$")
    rx_tagged = re.compile(r"^\s*VLAN passing  : (?P<tagged>.+)$")
    rx_tag = re.compile(r"^\s*Tagged\s+VLAN ID :\s+(?P<tagged>.+)$")
    rx_untag = re.compile(r"^\s*Untagged\s+VLAN ID :\s+(?P<untagged>.+)$")
    rx_channel_description = re.compile(
        r"^(?P<interface>Po\d+)\s+((?P<description>\S+)|)$", re.MULTILINE)
    rx_vlan_stack = re.compile(
        r"^(?P<interface>\S+)\s+(?P<role>\S+)\s*$", re.IGNORECASE)  # TO DO

    def execute(self):

        # Get portchannels
        portchannel_members = []
        portchannels = self.scripts.get_portchannel()
        for p in portchannels:
            portchannel_members += p["members"]

        #TODO
        # Get 802.1ad status if supported
        vlan_stack_status = {}
        """
        try:
            cmd = self.cli("show vlan-stacking")
            for match in self.rx_vlan_stack.finditer(cmd):
                if match.group("role").lower() == "tunnel":
                    vlan_stack_status[int(match.group("interface"))] = True
        except self.CLISyntaxError:
            pass
        """

        # Try snmp first
        if self.has_snmp():
            try:

                # Get interafces status
                interface_status = {}
                for s in self.scripts.get_interface_status():
                    interface_status[s["interface"]] = s["status"]

                # Get switchport index, name and description
                iface_name = {}
                iface_descr = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.31.1.1.1.1",
                    "1.3.6.1.2.1.31.1.1.1.18"], bulk=True):
                    iface = v[1].replace('GigabitEthernet', 'Gi ')
                    iface = iface.replace('Bridge-Aggregation', 'Po ')
                    iface_name.update({v[0]: iface})
                    iface_descr.update({iface: v[2]})

                # Make a list of tags for each interface or portchannel
                port_vlans = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.7.1.4.3.1.1",
                    "1.3.6.1.2.1.17.7.1.4.3.1.2",
                    "1.3.6.1.2.1.17.7.1.4.3.1.4"], bulk=True):
                    tagged = v[2]
                    untagged = v[3]

                    s = self.hex_to_bin(untagged)
                    un = []
                    for i in range(len(s)):
                        if i + 1 > len(iface_name):
                            break
                        if s[i] == '1':
                            iface = iface_name[str(i + 1)]
                            if iface not in port_vlans:
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            port_vlans[iface]["untagged"] = v[0]
                            un += [str(i + 1)]

                    s = self.hex_to_bin(tagged)
                    for i in range(len(s)):
                        if s[i] == '1' and str(i + 1) not in un and i + 1 <= len(iface_name):
                            iface = iface_name[str(i + 1)]
                            if iface not in port_vlans:
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            port_vlans[iface]["tagged"].append(v[0])

                # Get switchport data and overall result
                r = []
                swp = {}
                write = False
                for name in interface_status:
                    name = name.replace('GigabitEthernet', 'Gi ')
                    name = name.replace('Bridge-Aggregation', 'Po ')
                    if name in portchannel_members:
                        for p in portchannels:
                            if name in p["members"]:
                                name = p["interface"]
                                status = False
                                for interface in p["members"]:
                                    if interface_status.get(interface):
                                        status = True
                                description = name + ' Interface'
                                if not description:
                                    description = ''
                                members = p["members"]
                                portchannels.remove(p)
                                write = True
                                if name not in port_vlans:
                                    port_vlans.update(
                                        {name: {
                                            "tagged": port_vlans[p["members"][0]]["tagged"],
                                            "untagged": port_vlans[p["members"][0]]["untagged"],
                                            }
                                        })
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
        # Make a list of tags for each interface or portchannel
        port_vlans = {}
        port_channels = portchannels

        r = []
        swp = {}
        write = False
        ifaces = self.cli("display interface")
        ifaces = ifaces.splitlines()
        for i in range(len(ifaces)):
            match = self.rx_iface.search(ifaces[i])
            if match:
                name = match.group("iface")
                name = name.replace('GigabitEthernet', 'Gi ')
                name = name.replace('Bridge-Aggregation', 'Po ')
                status = match.group("status") == 'UP'
                if name in portchannel_members:
                    for p in portchannels:
                        if name in p["members"]:
                            name = p["interface"]
                            rx_po = re.compile(
                                r"^\s*Bridge-Aggregation" + name.split(' ')[1] + " current state:\s+(?P<status>(UP|DOWN|Administratively DOWN))$",
                                re.IGNORECASE)
                            j = 0
                            match = rx_po.search(ifaces[j])
                            while not match:
                                j += 1
                                match = rx_po.search(ifaces[j])
                            status = match.group("status") == 'UP'
                            j += 2
                            description = ifaces[j].split(' Description: ')[1]
                            if not description:
                                description = ''
                            members = p["members"]
                            portchannels.remove(p)
                            write = True
                            if name not in port_vlans:
                                port_vlans.update({name: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            j += 2
                            while not self.rx_type.search(ifaces[j]):
                                j += 1
                            match = self.rx_type.search(ifaces[j])
                            vtype = match.group("type")
                            j += 1
                            if vtype == "trunk":
                                match = self.rx_tagged.search(ifaces[j])
                                tagged = match.group("tagged")
                                tagged = tagged.replace('(default vlan)', '')
                                port_vlans[name]["tagged"] =  self.expand_rangelist(tagged)
                            else:
                                match = self.rx_tag.search(ifaces[j])
                                tagged = match.group("tagged")
                                if 'none' not in tagged:
                                    port_vlans[name]["tagged"] =  self.expand_rangelist(tagged)
                                j += 1
                                match = self.rx_untag.search(ifaces[j])
                                untagged = match.group("untagged")
                                if untagged is not 'none':
                                    port_vlans[name]["untagged"] = int(untagged.split(',')[0])
                                j += 1
                            i += 9
                        break
                else:
                    if name not in port_vlans:
                        port_vlans.update({name: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                    i += 2
                    match = self.rx_description.search(ifaces[i])
                    if match:
                        description = match.group("description")
                    else:
                        description = ''
                    while not self.rx_type.search(ifaces[i]):
                        i += 1
                    match = self.rx_type.search(ifaces[i])
                    vtype = match.group("type")
                    i += 1
                    if vtype == "trunk":
                        match = self.rx_tagged.search(ifaces[i])
                        tagged = match.group("tagged")
                        tagged = tagged.replace('(default vlan)', '')
                        port_vlans[name]["tagged"] = self.expand_rangelist(tagged)
                    else:
                        match = self.rx_tag.search(ifaces[i])
                        tagged = match.group("tagged")
                        if 'none' not in tagged:
                            port_vlans[name]["tagged"] = self.expand_rangelist(tagged)
                        i += 1
                        match = self.rx_untag.search(ifaces[i])
                        untagged = match.group("untagged")
                        if untagged is not 'none':
                            port_vlans[name]["untagged"] = int(untagged.split(',')[0])
                        i += 1
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
