# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve9xxx.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaces


class Script(noc.sa.script.Script):
    name = "HP.ProCurve9xxx.get_interfaces"
    implements = [IGetInterfaces]

    rx_sh_int = re.compile(r"^(?P<interface>.+?)\s+is\s+(?P<admin_status>up|down),\s+line\s+protocol\s+is\s+(?P<oper_status>up|down)", re.MULTILINE | re.IGNORECASE)
    rx_int_alias = re.compile(r"^(Description|Vlan alias name is)\s*(?P<alias>.*?)$", re.MULTILINE | re.IGNORECASE)
    rx_int_mac = re.compile(r"address\s+is\s+(?P<mac>\S+)", re.MULTILINE | re.IGNORECASE)
    rx_int_ipv4 = re.compile(r"Internet address is (?P<address>[0-9\.\/]+)", re.MULTILINE | re.IGNORECASE)
    rx_vlan_list = re.compile(r"untagged|(?P<from>\w+\s[0-9\.\/]+)(?P<to>\sto\s[0-9\.\/]+)?", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        portchannel_members = {}  # member -> (portchannel, type)
        for pc in self.scripts.get_portchannel():
            i = pc["interface"]
            for m in pc["members"]:
                # 9xxx doesn't support LACP
                portchannel_members[m] = (i, False)

        interfaces = []
        shospf = self.cli("sh ip ospf interface")
        ospfint = []
        for s in shospf.split("\n"):
            if s.find("OSPF enabled") > 0:
                i = s.split(',')[0]
                if i[0] == 'v':
                    ospfint.append('ve' + i[1:])
                else:
                    ospfint.append(i)

        shrunvlan = self.cli("sh running-config vlan")
        tagged = {}
        untagged = {}
        r = []
        for v in shrunvlan.split('!'):
#            if v[1:5] == 'vlan':
#               vlan = v.split('\n')[1].split(' ')[1]
            match = self.rx_vlan_list.findall(v)
            if match:
                tag = 1
                m2 = match
                for m in match:
                    if not m[0]:
                        tag = 0
                        continue

                    if m[0].split()[0] == "vlan":
                        vlan = m[0].split()[1]
                        continue

                    elif m[0][:3] == "ve ":
                        ifc = '' . join(m[0].split())
                        if untagged.has_key(ifc):
                            untagged[ifc].append(vlan)
                        else:
                            untagged[ifc] = vlan
                            continue

                    elif not m[0].split()[0] == 'ethe':
                        continue

                    elif not m[1]:
                        ifc = m[0].split()[1]
                        if tag == 1:
                            if tagged.has_key(ifc):
                                tagged[ifc].append(vlan)
                            else:
                                tagged[ifc] = [vlan]
                        else:
                            untagged[ifc] = vlan

                    else:
                        first = m[0].split()[1].split('/')[1]
                        last = m[1].split()[1].split('/')[1]
                        for n in range(int(first), int(last) + 1):
                            ifc = m[0].split()[1].split('/')[0] + '/' + repr(n)
                            if tag == 1:
                                if tagged.has_key(ifc):
                                    tagged[ifc].append(vlan)
                                else:
                                    tagged[ifc] = [vlan]

                            else:
                                untagged[ifc] = vlan

#                    l = v[a:].split('\n')[0].split()
#                    tagged[l[1]] = vlan
#                a = v.find('router-interface')
#                if a > 0:
#                    i = v[a:].split(' ')
#                    untagged[i[1]+i[2][:-1]] =  vlan

        v = self.cli("show interfaces brief")
        for s in v.split("\n"):
                if not s or s[0:4] == "Port":
                    continue
                ifname = s.split()[0]
                f2l = ifname[0:2]
                if f2l == "ve":
                    ift = "SVI"
                elif f2l == "lb":
                    ift = "loopback"
                else:
                    ift = "physical"
                admin_status = s.split()[1] == "Up"
                oper_status = admin_status
                if len(s.split()) > 9:
                    desc = s.split()[9]
                else:
                    desc = ''

                iface = {
                    "name": ifname,
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "type": ift,
                    "description": desc
                }
                mac = s.split()[8]
                if not mac == 'N/A':
                    iface["mac"] = mac
                # Process portchannel members
                if ifname in portchannel_members:
                    iface["aggregated_interface"] = portchannel_members[ifname][0]
                # Process subinterfaces
                subinterfaces = []
                enabled_afi = []
                enabled_protocols = []
                if "aggregated_interfac" not in iface:
                    sub = {
                        "name": ifname,
                        "admin_status": admin_status,
                        "oper_status": oper_status
                    }

                    if untagged.has_key(ifname):
                            sub["untagged_vlan"] = untagged[ifname]
                    if tagged.has_key(ifname):
                            sub["tagged_vlan"] = tagged[ifname]

                    if ift == "SVI":  # IPv4 addresses
                        shint = self.cli("show interfaces %s" % ifname)
                        for str in shint.split("\r\n"):
                            match = self.rx_int_ipv4.search(str)
                            if match:
                                enabled_afi += ["IPv4"]
                                sub["ipv4_addresses"] = [match.group("address")]

                    if ift == "physical":
                        enabled_afi += ["BRIDGE"]

                    if ifname in ospfint:
                        enabled_protocols += ["OSPF"]

                    sub["enabled_afi"] = enabled_afi
                    sub["enabled_protocols"] = enabled_protocols

                    if len(enabled_afi) > 0:
                        subinterfaces += [sub]
                # Append to interfaces
                iface["subinterfaces"] = subinterfaces
                if "subinterfaces" or "aggregated_interface" in iface:
                    interfaces += [iface]
            # Get interfaces
        return [{"interfaces": interfaces}]
