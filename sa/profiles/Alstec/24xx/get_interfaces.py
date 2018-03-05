# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "Alstec.24xx.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s*(?P<port>\d+/\d+)\s+(?P<admin_status>\S+)\s+\S+\s+"
        r"(?P<oper_status>\S+)", re.MULTILINE)
    rx_desc = re.compile(
        r"^\s*(?P<port>\d+/\d+)\s+(?:Enable|Disable)\s+(?:Up|Down)\s+"
        r"(?P<desc>\S+)$", re.MULTILINE)
    rx_vlan = re.compile(
        r"^interface (?P<port>\d+/\d+)\s*\n"
        r"(^vlan pvid (?P<pvid>\d+)\s*\n)?"
        r"^vlan participation include \S+\s*\n"
        r"(^vlan tagging (?P<tagged>\S+)\s*\n)?",
        re.MULTILINE)
    rx_ip = re.compile(
        r"^IP Address\.+ (?P<ip_address>\S+)\s*\n"
        r"^Subnet Mask\.+ (?P<ip_subnet>\S+)\s*\n"
        r"^Default Gateway\.+ \S+\s*\n"
        r"^IPv6 AutoConfig Mode\.+ \S+\s*\n"
        r"^IPv6 address\.+ (?P<ipv6_address>\S+)\s*\n"
        r"^MAC Address\.+ (?P<mac>\S+)\s*\n"
        r"^Management VLAN ID\.+ (?P<vlan_id>\d+)\s*\n",
        re.MULTILINE)
    rx_ip2 = re.compile(
        r"^\s*IP Address\s*\.+ (?P<ip_address>\S+)\s*?"
        r"^\s*Subnet Mask\s*\.+ (?P<ip_subnet>\S+)\s*.+"
        r"^\s*(MAC Address|Burned In MAC Address)\s*\.+ (?P<mac>\S+)\s*.+"
        r"^\s*Management VLAN ID\s*\.+ (?P<vlan_id>\d+)\s*\n",
        re.MULTILINE | re.DOTALL)
    rx_ipv6 = re.compile(
        r"^(IPv6 address|IPv6 Prefix is )\.+ (?P<ipv6_address>\S+)\s*",
        re.MULTILINE)

    def execute(self):
        c = self.scripts.get_config()
        d = self.cli("show port description all", ignore_errors=True)
        interfaces = []
        snmp_ifindex = 1  # Dirty hack. I can not found another way
        for match in self.rx_port.finditer(self.cli("show port all")):
            ifname = match.group("port")
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": match.group("admin_status") == "Enable",
                "oper_status": match.group("oper_status") == "Up",
                "enabled_protocols": [],
                "snmp_ifindex": snmp_ifindex,
                "subinterfaces": [{
                    "name": ifname,
                    "admin_status": match.group("admin_status") == "Enable",
                    "oper_status": match.group("oper_status") == "Up",
                    "enabled_afi": ["BRIDGE"]
                }]
            }
            for matchd in self.rx_desc.finditer(d):
                if matchd.group("port") == ifname:
                    iface["description"] = matchd.group("desc")
                    iface["subinterfaces"][0]["description"] = matchd.group("desc")
            for match1 in self.rx_vlan.finditer(c):
                if match1.group("port") == ifname:
                    if match1.group("pvid"):
                        iface["subinterfaces"][0]["untagged_vlan"] = \
                            match1.group("pvid")
                    if match1.group("tagged"):
                        iface["subinterfaces"][0]["tagged_vlans"] = \
                            self.expand_rangelist(match1.group("tagged"))
            interfaces += [iface]
            snmp_ifindex += 1
        v = self.cli("show network", cached=True)
        match = self.rx_ip2.search(v)
        ip_address = match.group("ip_address")
        ip_subnet = match.group("ip_subnet")
        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
        iface = {
            "name": "0/0",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "mac": match.group("mac"),
            "enabled_protocols": [],
            "subinterfaces": [{
                "name": "0/0",
                "admin_status": True,
                "oper_status": True,
                "mac": match.group("mac"),
                "enabled_afi": ['IPv4'],
                "ipv4_addresses": [ip_address],
                "vlan_ids": [int(match.group("vlan_id"))]
            }]
        }
        match = self.rx_ipv6.search(v)
        if match:
            iface["subinterfaces"][0]["enabled_afi"] += ['IPv6']
            iface["subinterfaces"][0]["ipv6_addresses"] = [match.group("ipv6_address")]
        interfaces += [iface]
        return [{"interfaces": interfaces}]
