# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
 
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    name = "DLink.DxS.get_interfaces"
    implements = [IGetInterfaces]

    TIMEOUT = 300

    rx_ipif1 = re.compile(r"Interface Name\s+:\s+(?P<ifname>.+?)\s*\n"
    r"IP Address\s+:\s+(?P<ip_address>\S+)\s+\(Manual\)\s*\n"
    r"Subnet Mask\s+:\s+(?P<ip_subnet>\S+)\s*\n"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
    r"Admin. State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n"
    r"Member Ports\s+:\s*\S*\s*\n"
    r"(DHCP Option12 State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(DHCP Option12 Host Name\s+:\s*\S*\s*\n)?"
    r"(Description\s+:\s*(?P<desc>\S*?)\s*\n)?",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_ipif2 = re.compile(r"IP Interface\s+:\s+(?P<ifname>.+?)\s*\n"
    r"VLAN Name\s+:\s+(?P<vlan_name>\S+)\s*\n"
    r"Interface Admin.? State\s+:\s+(?P<admin_state>Enabled|Disabled)\s*\n"
    r"(DHCPv6 Client State\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(Link Status\s+:\s+(?P<oper_status>Link\s*UP|Link\s*Down)\s*\n)?"
    r"(IPv4 Address\s+:\s+(?P<ipv4_address>\S+)\s+\(Manual\)\s+Primary\s*\n)?"
    r"(Proxy ARP\s+:\s+(?:Enabled|Disabled)\s+\(Local : \S+\s*\)\s*\n)?"
    r"(IPv4 State\s+:\s+(?P<is_ipv4>Enabled|Disabled)\s*\n)?"
    r"(IPv6 State\s+:\s+(?P<is_ipv6>Enabled|Disabled)\s*\n)?"
    r"(IP Directed Broadcast\s+:\s+(?:Enabled|Disabled)\s*\n)?"
    r"(IP MTU\s+:\s+\d+\s+\n)?",
    re.IGNORECASE | re.MULTILINE | re.DOTALL)

    rx_link_up = re.compile(r"Link\s*UP", re.IGNORECASE)

    def execute(self):
        ports = self.profile.get_ports(self)
        vlans = self.profile.get_vlans(self)
        fdb = self.scripts.get_mac_address_table()
        interfaces = []
        for p in ports:
            i = {
                "name": p['port'],
                "type": "physical",
                "admin_status": p['admin_state'],
                "oper_status": p['status'],
                "subinterfaces": [{
                    "name": p['port'],
                    "admin_status": p['admin_state'],
                    "oper_status": p['status'],
                    # "ifindex": 1,
                    "is_bridge": True
                }]
            }
            desc = p['desc']
            if desc != '' and desc != 'null':
                i.update({"description" : desc})
                i['subinterfaces'][0].update({"description" : desc})
            tagged_vlans = []
            for v in vlans:
                if p['port'] in v['tagged_ports']:
                    tagged_vlans += [v['vlan_id']]
                if p['port'] in v['untagged_ports']:
                    i['subinterfaces'][0].update({
                        "untagged_vlan" : v['vlan_id']
                    })
                if len(tagged_vlans) != 0:
                    i['subinterfaces'][0].update({
                        "tagged_vlan" : tagged_vlans
                    })
            interfaces += [i]

        ipif = self.cli("show ipif")
        for match in self.rx_ipif1.finditer(ipif):
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            oper_status = re.match(self.rx_link_up, o_status) is not None
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                    "is_ipv4": True
                }]
            }
            desc = match.group("desc")
            if desc is not None and desc != '':
                desc = desc.strip()
                i.update({"description" : desc})
                i['subinterfaces'][0].update({"description" : desc})
            ip_address = match.group("ip_address")
            ip_subnet = match.group("ip_subnet")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            i['subinterfaces'][0].update({"ipv4_addresses" : [ip_address]})
            vlan_name = match.group("vlan_name")
            for v in vlans:
                if vlan_name == v['vlan_name']:
                    vlan_id = v['vlan_id']
                    i['subinterfaces'][0].update({"vlan_ids" : [vlan_id]})
                    for f in fdb:
                        if 'CPU' in f['interfaces'] \
                        and vlan_id == f['vlan_id']:
                            i.update({"mac" : f['mac']})
                            i['subinterfaces'][0].update({"mac" : f['mac']})
                            break
                    break
            interfaces += [i]

        for match in self.rx_ipif2.finditer(ipif):
            admin_status = match.group("admin_state") == "Enabled"
            o_status = match.group("oper_status")
            if o_status is not None:
                oper_status = re.match(self.rx_link_up, o_status) is not None
            else:
                oper_status = admin_status
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": admin_status,
                    "oper_status": oper_status,
                }]
            }
            ipv4 = match.group("is_ipv4")
            if ipv4 is not None:
                i['subinterfaces'][0].update({
                    "is_ipv4" : ipv4 == "Enabled"
                })
            ipv6 = match.group("is_ipv6")
            if ipv6 is not None:
                i['subinterfaces'][0].update({
                    "is_ipv6" : ipv6 == "Enabled"
                })
            # TODO: Parse secondary IPv4 address and IPv6 address
            ipv4_address = match.group("ipv4_address")
            if ipv4_address is not None:
                i['subinterfaces'][0].update({
                    "ipv4_addresses" : [ipv4_address]
                })
                if ipv4 is None:
                    i['subinterfaces'][0].update({
                        "is_ipv4" : True
                    })
            vlan_name = match.group("vlan_name")
            for v in vlans:
                if vlan_name == v['vlan_name']:
                    vlan_id = v['vlan_id']
                    i['subinterfaces'][0].update({"vlan_ids" : [vlan_id]})
                    for f in fdb:
                        if 'CPU' in f['interfaces'] \
                        and vlan_id == f['vlan_id']:
                            i.update({"mac" : f['mac']})
                            i['subinterfaces'][0].update({"mac" : f['mac']})
                            break
                    break
            interfaces += [i]

        return [{"interfaces": interfaces}]
