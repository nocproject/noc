# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_interfaces
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetInterfaces
from noc.lib.ip import IPv4


class Script(NOCScript):
    name = "DLink.DES21xx.get_interfaces"
    implements = [IGetInterfaces]
    rx_swi = re.compile(
        r"IP Address:(?P<ip>\S+)\s*\nSubnet mask:(?P<mask>\S+)\s*\n"
        r".+?MAC address:(?P<mac>\S+)\s*\n", re.DOTALL)
    rx_mv = re.compile(r"MANAGEMENT VLAN:\s+(?P<mv>\d+)", re.IGNORECASE)

    def execute(self):
        sw = self.scripts.get_switchport()
        ports = self.scripts.get_interface_status()
        mv = self.rx_mv.search(self.cli("show vlan", cached=True))
        if mv:
            mv = int(mv.group("mv"))
        else:
            mv = 1
        interfaces = []
        for p in ports:
            ifname = p['interface']
            i = {
                "name": ifname,
                "type": "physical",
                "oper_status": p['status'],
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": ifname,
                    "oper_status": p['status'],
                    # "ifindex": 1,
                    "enabled_afi": ['BRIDGE']
                }]
            }
            for p1 in sw:
                if p1['interface'] == ifname:
                    i['subinterfaces'][0]['tagged_vlans'] = p1['tagged']
                    if 'untagged' in p1:
                        i['subinterfaces'][0]['untagged_vlan'] = p1['untagged']
            interfaces += [i]
        match = self.rx_swi.search(self.cli("show switch"))
        if match:
            i = {
                "name": "System",
                "type": "SVI",
                "oper_status": True,
                "admin_status": True,
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": "System",
                    "oper_status": True,
                    "admin_status": True,
                    "mac": match.group("mac"),
                    "vlan_ids": [mv],
                    "enabled_afi": ['IPv4']
                }]
            }
            addr = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
            i['subinterfaces'][0]["ipv4_addresses"] = [ip_address]
            interfaces += [i]

        return [{"interfaces": interfaces}]
