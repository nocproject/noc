# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.1905.get_switchport
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import time
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetSwitchport


class Script(NOCScript):
    name = "HP.1905.get_switchport"
    implements = [IGetSwitchport]

    def execute(self):

        # Get portchannels
        portchannel_members = []
        try:
            portchannels = self.scripts.get_portchannel()
            for p in portchannels:
                portchannel_members += p["members"]
        except:
            pass

        # Get interafces status
        interface_status = {}
        port_vlans = {}
        for s in self.scripts.get_interface_status():
            interface_status[s["interface"]] = s["status"]

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
        if self.snmp and self.access_profile.snmp_ro:
            try:
                # Make a list of tags for each interface or portchannel
                port_vlans = {}
                for v in self.snmp.get_tables(
                    ["1.3.6.1.2.1.17.7.1.4.2.1.3",
                    "1.3.6.1.2.1.17.7.1.4.2.1.4",
                    "1.3.6.1.2.1.17.7.1.4.2.1.5"], bulk=True):
                    tagged = v[2]
                    untagged = v[3]

                    s = self.hex_to_bin(untagged)
                    print s
                    un = []
                    for i in range(len(s)):
                        if s[i] == '1':
                            if i + 1 < 25:
                                iface = 'Ethernet0/' + str(i + 1)
                            else:
                                iface = 'Copper0/' + str(i + 1)
#                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
#                            iface = self.snmp.get(oid, cached=True)
#                            if not iface:
#                                oid = "1.3.6.1.2.1.2.2.1.2." + str(i + 1)
#                                iface = self.snmp.get(oid, cached=True)
                            if iface not in port_vlans:
                                port_vlans.update(
                                    {iface: {
                                        "tagged": [],
                                        "untagged": '',
                                        }
                                    })
                            port_vlans[iface]["untagged"] = v[1]
                            un += [str(i + 1)]

                    s = self.hex_to_bin(tagged)
                    for i in range(len(s)):
                        if s[i] == '1' and str(i + 1) not in un:
                            if i + 1 < 25:
                                iface = 'Ethernet0/' + str(i + 1)
                            else:
                                iface = 'Copper0/' + str(i + 1)
#                            oid = "1.3.6.1.2.1.31.1.1.1.1." + str(i + 1)
#                            iface = self.snmp.get(oid, cached=True)
#                            if not iface:
#                                oid = "1.3.6.1.2.1.2.2.1.2." + str(i + 1)
#                                iface = self.snmp.get(oid, cached=True)
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
            except self.snmp.TimeOutError:
                time.sleep(2)
                port_descr = {}
                try:
                    for iface, description in self.snmp.join_tables(
                        "1.3.6.1.2.1.2.2.1.2", "1.3.6.1.2.1.2.2.1.2",
                        bulk=True):
                        port_descr.update({iface: description})
                except self.snmp.TimeOutError:
                    raise Exception("Not implemented")

            try:
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

        # Fallback to CLI
        raise Exception("Not implemented")
