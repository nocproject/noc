# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

# Python modules
from __future__ import with_statement
import re
# NOC modules
import noc.sa.script
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(noc.sa.script.Script):
    name = "DLink.DxS_Smart.get_interfaces"
    implements = [IGetInterfaces]

    rx_ipif = re.compile(r"IP Address\s+:\s+(?P<ip_address>\S+)\s*\n"
    r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_mgmt_vlan = re.compile(
        r"^802.1Q Management VLAN\s+: (?P<vlan>\S+)\s*\n")

    def execute(self):
        interfaces = []
        # Get portchannes
        portchannel_members = {}  # member -> (portchannel, type)
        # with self.cached():
        #    for pc in self.scripts.get_portchannel():
        #        i = pc["interface"]
        #        t = pc["type"] == "L"
        #        for m in pc["members"]:
        #            portchannel_members[m] = (i, t)
        admin_status = {}
        if self.snmp and self.access_profile.snmp_ro:
            try:
                for n, s in self.snmp.join_tables(
                        "1.3.6.1.2.1.31.1.1.1.1",
                        "1.3.6.1.2.1.2.2.1.7", bulk=True):  # IF-MIB
                    if n[:3] == 'Aux' or n[:4] == 'Vlan' \
                    or n[:11] == 'InLoopBack':
                        continue
                    else:
                        admin_status.update({n: int(s) == 1})
            except self.snmp.TimeOutError:
                pass
        else:
            ports = self.profile.get_ports(self)
            for p in ports:
                admin_status.update({p['port']: p['admin_state']})

        # Get switchports
        for swp in self.scripts.get_switchport():
            admin = admin_status[swp["interface"]]
            name = swp["interface"]
            iface = {
                "name": name,
                "type": "aggregated" if len(swp["members"]) > 0
                else "physical",
                "admin_status": admin,
                "oper_status": swp["status"],
                # "mac": mac,
                "subinterfaces": [{
                    "name": name,
                    "admin_status": admin,
                    "oper_status": swp["status"],
                    "enabled_afi": ['BRIDGE'],
                    # "mac": mac,
                    # "snmp_ifindex": self.scripts.get_ifindex(interface=name)
                }]
            }
            if swp["tagged"]:
                iface["subinterfaces"][0]["tagged_vlans"] = swp["tagged"]
            try:
                iface["subinterfaces"][0]["untagged_vlan"] = swp["untagged"]
            except KeyError:
                pass
            if 'description' in swp:
                iface["description"] = swp["description"]
            if name in portchannel_members:
                iface["aggregated_interface"] = portchannel_members[name][0]
                if portchannel_members[name][1]:
                    n["enabled_protocols"] = ["LACP"]
            interfaces += [iface]

        ipif = self.cli("show ipif")
        match = self.rx_ipif.search(ipif)
        if match:
            i = {
                "name": "System",
                "type": "SVI",
                "admin_status": True,
                "oper_status": True,
                "subinterfaces": [{
                    "name": "System",
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["IPv4"]
                }]
            }
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = \
                "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            ch_id = self.scripts.get_chassis_id()
            i["mac"] = ch_id[0]['first_chassis_mac']
            i['subinterfaces'][0]["mac"] = ch_id[0]['first_chassis_mac']
            mgmt_vlan = 1
            sw = self.cli("show switch", cached=True)
            match = self.rx_mgmt_vlan.search(ipif)
            if match:
                vlan = match.group("vlan")
                if vlan != "Disabled":
                    vlans = self.profile.get_vlans(self)
                    for v in vlans:
                        if vlan == v['name']:
                            mgmt_vlan = int(v['vlan_id'])
                            break
            # Need hardware to testing
            i['subinterfaces'][0].update({"vlan_ids": [mgmt_vlan]})
            interfaces += [i]

        return [{"interfaces": interfaces}]
