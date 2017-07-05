# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSCComm.LPOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "NSCComm.LPOS.get_interfaces"
    interface = IGetInterfaces

    rx_ip = re.compile(
        r"^\s+Physical Address.+: (?P<mac>\S+)\s*\n"
        r"^\s+IP Address.+: (?P<ip_address>\S+)\s*\n"
        r"^\s+Subnet Mask.+: (?P<ip_subnet>\S+)\s*\n"
        r"^\s+Default Gateway.+: \S+\s*\n"
        r"^\s+VLAN ID,PRI.+: (?P<vlan_id>\d+),\d+\s*\n",
        re.MULTILINE
    )
    rx_eth = re.compile(r"^\s+(?P<name>\d+)", re.MULTILINE)

    def execute(self):
        interfaces = []
        v = self.cli("ethstat")
        for match in self.rx_eth.finditer(v):
            iface = {
                "name": match.group("name"),
                "type": "physical",
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": match.group("name"),
                    "enabled_afi": ["BRIDGE"],
                    "tagged_vlans": []
                }]
            }
            interfaces += [iface]
        v = self.cli("ipconfig")
        match = self.rx_ip.search(v)
        ip_address = match.group("ip_address")
        ip_subnet = match.group("ip_subnet")
        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
        iface = {
            "name": "MGMT",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "enabled_protocols": [],
            "subinterfaces": [{
                "name": "MGMT",
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ['IPv4'],
                "ipv4_addresses": [ip_address],
                "vlan_ids": [int(match.group("vlan_id"))]
            }]
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
