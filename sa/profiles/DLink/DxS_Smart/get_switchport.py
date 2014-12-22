# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_switchport
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
    name = "DLink.DxS_Smart.get_switchport"
    implements = [IGetSwitchport]

    def execute(self):
        r = []
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
#        try:
#            stack = self.cli("show vlan-stacking")
#            for match in self.rx_vlan_stack.finditer(stack):
#                if match.group("role").lower() == "tunnel":
#                    vlan_stack_status[int(match.group("interface"))] = True
#        except self.CLISyntaxError:
#            pass

        # Try snmp first
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
                pmib = self.profile.get_pmib(self.scripts.get_version())
                if pmib is None:
                    raise NotImplementedError()
                for v in self.snmp.get_tables(
                    [pmib + ".7.6.1.1", pmib + ".7.6.1.2", pmib + ".7.6.1.4"],
                        bulk=True):
                    tagged = v[2]
                    untagged = v[3]

#                    s = self.hex_to_bin(untagged)
                    s = hex2bin(untagged)
                    un = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            if iface not in port_vlans:
                                port_vlans.update({
                                    iface: {
                                        "tagged": [],
                                        "untagged": '',
                                    }
                                })
                            port_vlans[iface]["untagged"] = v[0]
                            un += [str(i + 1)]

#                    s = self.hex_to_bin(tagged)
                    s = hex2bin(tagged)
                    for i in range(len(s)):
                        if s[i] == '1' and str(i + 1) not in un:
                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
                            iface = self.snmp.get(oid, cached=True)
                            if iface not in port_vlans:
                                port_vlans.update({
                                    iface: {
                                        "tagged": [],
                                        "untagged": '',
                                    }
                                })
                            port_vlans[iface]["tagged"].append(v[0])

                # Get switchport description
                port_descr = {}
                for iface, description in self.snmp.join_tables(
                    "1.3.6.1.2.1.31.1.1.1.1", "1.3.6.1.2.1.31.1.1.1.18",
                        bulk=True):
                    port_descr.update({iface: description})

                # Get switchport data and overall result
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
                            "802.1Q Enabled":
                                len(port_vlans.get(name, '')) > 0,
                            "802.1ad Tunnel":
                                vlan_stack_status.get(name, False),
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

        return r
