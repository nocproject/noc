# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Qtech.QSW.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "Qtech.QSW.get_switchport"
    implements = [IGetSwitchport]

    rx_interface = re.compile(
        r"^\s*Ethernet\s+(?P<interface>\S+)\s+is\s+(enabled|disabled),\s+port\s+link\s+is\s+(up|down)")
    rx_mode = re.compile(r"^\s*Port\s+mode\s*:\s*(?P<mode>\S+)$")
    rx_vlan_t = re.compile(r"^\s*Vlan\s+allowed\s*:\s*(?P<vlans>\S+)$")
    rx_vlan_at = re.compile(r"^\s*Tagged\s+VLAN\s+ID\s*:\s*(?P<vlans>\S+)$")
    rx_vlan_au = re.compile(r"^\s*Untagged\s+VLAN\s+ID\s*:\s*(?P<vlans>\S+)$")

    rx_description = re.compile(
        r"^\s*(?P<interface>e\S+)\s+((?P<description>(\S+ \S+|\S+))|)$",
        re.MULTILINE)
#    rx_channel_description = re.compile(
#        r"^(?P<interface>Po\d+)\s+((?P<description>\S+)|)$", re.MULTILINE)
#    rx_vlan_stack = re.compile(
#        r"^(?P<interface>\S+)\s+(?P<role>\S+)\s*$", re.IGNORECASE)  # TODO


    def execute(self):

        #TODO
        # Get portchannels
#        portchannels = self.scripts.get_portchannel()
        portchannels = []
        portchannel_members = []
#        for p in portchannels:
#            portchannel_members += p["members"]

        # Get interafces status
        interface_status = {}
        port_vlans = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

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
        """
        # SNMP not working!
        if self.snmp and self.access_profile.snmp_ro:
            def hex2bin(ports):
                bin = [
                    '0000', '0001', '0010', '0011',
                    '0100', '0101', '0110', '0111',
                    '1000', '1001', '1010', '1011',
                    '1100', '1101', '1110', '1111',
                    ]
                ports = ["%02x" % ord(c) for c in ports]
                p = ''
                for c in ports:
                   for i in range(len(c)):
                        p += bin[int(c[i], 16)]
                return p
            try:
                # Make a list of tags for each interface or portchannel
                port_vlans = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.7.1.4.2.1.3",
                    "1.3.6.1.2.1.17.7.1.4.2.1.4",
                    "1.3.6.1.2.1.17.7.1.4.2.1.5"], bulk=True):
                    tagged = v[2]
                    untagged = v[3]

                    s = hex2bin(untagged)
                    un = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            if iface not in port_vlans:
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            port_vlans[iface]["untagged"] = v[1]
                            un += [str(i + 1)]

                    s = hex2bin(tagged)
                    for i in range(len(s)):
                        if s[i] == '1' and str(i + 1) not in un:
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            if iface not in port_vlans:
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            port_vlans[iface]["tagged"].append(v[1])

                # Get switchport description
                port_descr = {}
                for iface, description in self.snmp.join_tables(
                    "1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.31.1.1.1.18",
                    bulk=True):
                    port_descr.update({iface: description})

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
                                description = port_descr[name]
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
        """

        # Fallback to CLI
        # Make a list of tags for each interface or portchannel
        port_vlans = {}
        port_channels = portchannels


        iface_conf = self.cli("show interface")
        # Correct Qtech BUG:
        iface_conf = iface_conf.replace("\n\n                                                                          ", "\n")
        iface_conf = iface_conf.splitlines()
        i = 0
        L = len(iface_conf) - 2
        while i < L:
            match = self.rx_interface.match(iface_conf[i])
            if match:
                interface = match.group("interface")
            else:
                i += 1
                continue

            if interface in portchannel_members:
                for p in port_channels:
                    if interface in p["members"]:
                        interface = p["interface"]
                        port_channels.remove(p)
                        break
            if interface not in port_vlans:
                port_vlans.update({interface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                })

            i += 1
            match_mod = self.rx_mode.match(iface_conf[i])
            while not match_mod:
                i += 1
                match_mod = self.rx_mode.match(iface_conf[i])
            mode = match_mod.group("mode")

            i += 1
            if 'trunk' == mode:
                match = self.rx_vlan_t.match(iface_conf[i])
                if match:
                    vlans = match.group("vlans")
                    list_vlans = self.expand_rangelist(vlans)
                    port_vlans[interface]["tagged"] = list_vlans

            elif 'access' == mode or 'hybrid' == mode:
                match = self.rx_vlan_at.match(iface_conf[i])
                if match:
                    vlans = match.group("vlans")
                    list_vlans = self.expand_rangelist(vlans)
                    port_vlans[interface]["tagged"] = list_vlans

                i += 1
                match = self.rx_vlan_au.match(iface_conf[i])
                if match:
                    vlans = match.group("vlans")
                    port_vlans[interface]["untagged"] = vlans.split(',')[0]


        iface_conf = []
        # Why portchannels=[] ???????
        # Get portchannels onse more!!!
#        portchannels = self.scripts.get_portchannel()
        portchannels = []
        # Get switchport data and overall result
        r = []
        swp = {}
        write = False
        cmd = self.cli("show description interface")
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
                        cmd = "show description interface %s" % name
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
                swp["interface"] = self.profile.convert_interface_name(name)
                swp["members"] = members
                r.append(swp)
                write = False
        return r
