# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Zyxel.ZyNOS.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Zyxel.ZyNOS.get_switchport"
    implements = [IGetSwitchport]

    rx_portinfo = re.compile(r"Port No\s+:(?P<interface>\d+).\s*Active\s+:"
                                r"(?P<admin>\S+).\s*Name\s+:(?P<description>"
                                r"[A-Za-z0-9\-_/\.]*).\s*PVID\s+:"
                                r"(?P<untag>\d+)\s+Flow Control\s+:\S+$",
                                re.MULTILINE | re.DOTALL)
    rx_vlan_stack = re.compile(r"^(?P<interface>\d+)\s+(?P<role>\S+).+$",
                                re.MULTILINE)
    rx_vlan_stack_global = re.compile(r"^Operation:\s+(?P<status>active)$")
    rx_vlan_ports = re.compile(r"\s+\d+\s+(?P<vid>\d+)\s+\S+\s+\S+\s+"
                                r"Untagged\s+:(?P<untagged>(?:[0-9,\-])*)."
                                r"\s+Tagged\s+:(?P<tagged>(?:[0-9,\-])*)",
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

        # Try snmp first
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Make a list of tags for each interface
                port_vlans = {}
                # Join dot1qVlanFdbId, dot1qVlanCurrentEgressPorts
                # and dot1qVlanCurrentUntaggedPorts from QBridgeMib
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.7.1.4.2.1.3",
                     "1.3.6.1.2.1.17.7.1.4.2.1.4",
                     "1.3.6.1.2.1.17.7.1.4.2.1.5"], bulk=True):
                    tagged = v[2]
                    untagged = v[3]

                    s = self.hex_to_bin(untagged)
                    un = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1.%d" % (i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            # swpXX - regular port, enet0 - outband management
                            if 'swp' in iface:
                                # swp00 = 1st port etc...
                                iface = str(int(iface.split('swp')[1]) + 1)
                                if iface not in port_vlans:
                                    port_vlans.update({
                                        iface: {
                                            "tagged": [],
                                            "untagged": '',
                                        }
                                    })
                                port_vlans[iface]["untagged"] = v[1]
                                un += [str(i + 1)]

                    s = self.hex_to_bin(tagged)
                    for i in range(len(s)):
                        if s[i] == '1' and str(i + 1) not in un:
                            oid = "1.3.6.1.2.1.31.1.1.1.1.%d" % (i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            if 'swp' in iface:
                                iface = str(int(iface.split('swp')[1]) + 1)
                                if iface not in port_vlans:
                                    port_vlans.update({
                                        iface: {
                                            "tagged": [],
                                            "untagged": '',
                                        }
                                    })
                                port_vlans[iface]["tagged"].append(v[1])

                # Get switchports' description
                port_descr = {}
                for iface, description in self.snmp.join_tables(
                    "1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.31.1.1.1.18",
                    bulk=True):
                    if 'swp' in iface:
                        iface = str(int(iface.split('swp')[1]) + 1)
                    port_descr.update({iface: description})

                # Get switchports' data and overall result
                r = []
                swp = {}
                write = False
                for name in interface_status:
                    if name == "enet0":  # skip Outband management
                        continue         # 'cause it's not a switchport
                    if name in portchannel_members:
                        for p in portchannels:
                            if name in p["members"]:
                                description = port_descr[name]
                                if not description:
                                    description = ''
                                t = port_vlans[name]["tagged"]
                                u = port_vlans[name]["untagged"]
                                tun = vlan_stack_status.get(int(name), False)
                                name = p["interface"]
                                port_vlans[name] = {
                                    "tagged": t,
                                    "untagged": u
                                }
                                vlan_stack_status[name] = tun
                                status = False
                                for interface in p["members"]:
                                    if interface_status.get(interface):
                                        status = True
                                        break
                                members = p["members"]
                                portchannels.remove(p)
                                write = True
                                break
                    else:
                        if interface_status.get(name):
                            status = True
                        else:
                            status = False
                        description = port_descr[name]
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
        for match in self.rx_portinfo.finditer(self.cli("show interface " \
                                                        "config *")):
            name = match.group("interface")
            swp = {
                "status": interface_status.get(name, False),
                "description": match.group("description"),
                "802.1Q Enabled": len(port_tags[name].get("tags", None)) > 0,
                "802.1ad Tunnel": vlan_stack_status.get(int(name), False),
                "tagged": port_tags[name]["tags"],
            }
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
