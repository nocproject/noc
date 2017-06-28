# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.7200.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "Alstec.7200.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^(?P<port>\d+/\d+)\s+(\S+\s+)?(?P<admin_status>Enable|Disable)\s+"
        r"\S+\s+(\s+|100 Full\s+|1000 Full\s+)?"
        r"(?P<oper_status>Up|Down)\s+(?:Enable|Disable)", re.MULTILINE)
    rx_descr = re.compile(
        r"^Interface\.+\s*(?P<port>\d+/\d+)\s*\n"
        r"^ifIndex\.+ (?P<ifindex>\d+)\s*\n"
        r"^Description\.+(?P<descr>.*)\n"
        r"^MAC address\.+ (?P<mac>\S+)\s*\n"
        r"^Bit Offset Val\.+ \d+\s*\n", re.MULTILINE)
    rx_vlan = re.compile(
        r"^interface (?P<port>\d+/\d+)\s*\n"
        r"(^service-policy in \S+\s*\n)?"
        r"(^set (?P<igmp>igmp)\s*\n)?"
        r"(^set igmp mrouter interface\s*\n)?"
        r"(^vlan pvid (?P<pvid>\d+)\s*\n)?"
        r"^vlan participation include \S+\s*\n"
        r"(^vlan tagging (?P<tagged>\S+)\s*\n)?",
        re.MULTILINE)
    rx_ip = re.compile(
        r"^IP Address\.+ (?P<ip_address>\S+)\s*\n"
        r"^Subnet Mask\.+ (?P<ip_subnet>\S+)\s*\n"
        r"(^IP Address\.+ (?P<ip_address1>\S+)\s*\n)?"
        r"(^Subnet Mask\.+ (?P<ip_subnet1>\S+)\s*\n)?"
        r"^Default Gateway\.+ \S+\s*\n"
        r"(^IPv6 Administrative Mode\.+ \S+\s*\n)?"
        r"(^IPv6 Prefix is\s*\.+ (?P<ipv6_address>\S+)\s*\n)?"
        r"^Burned In MAC Address\.+ (?P<mac>\S+)\s*\n"
        r"^Locally Administered MAC address\.+ \S+\s*\n"
        r"^MAC Address Type.+\n"
        r"^Configured IPv4 Protocol\.+ \S+\s*\n"
        r"(^Configured IPv6 Protocol\.+ \S+\s*\n)?"
        r"(^IPv6 AutoConfig Mode\.+ \S+\s*\n)?"
        r"^Management VLAN ID\.+ (?P<vlan_id>\d+)\s*\n"
        r"(^Additional Management VLAN ID\.+ (?P<vlan_id1>\d+))?",
        re.MULTILINE | re.IGNORECASE)

    def execute(self):
        c = self.scripts.get_config()
        interfaces = []
        snmp_ifindex = 1  # Dirty hack. I can anot found another way
        for match in self.rx_port.finditer(self.cli("show port all")):
            ifname = match.group("port")
            try:
                v = self.cli("show port description %s" % ifname)
                match1 = self.rx_descr.search(v)
                snmp_ifindex = int(match1.group("ifindex"))
                mac = match1.group("mac")
                descr = match1.group("descr").strip()
            except self.CLISyntaxError:
                mac = ""
                descr = ""
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
                    "enabled_afi": ["BRIDGE"],
                    "enabled_protocols": []
                }]
            }
            if mac:
                iface["mac"] = mac
                iface["subinterfaces"][0]["mac"] = mac
            if descr:
                iface["description"] = descr
                iface["subinterfaces"][0]["description"] = descr
            for match1 in self.rx_vlan.finditer(c):
                if match1.group("port") == ifname:
                    if match1.group("pvid"):
                        iface["subinterfaces"][0]["untagged_vlan"] = \
                            match1.group("pvid")
                    if match1.group("tagged"):
                        iface["subinterfaces"][0]["tagged_vlans"] = \
                            self.expand_rangelist(match1.group("tagged"))
                    if match1.group("igmp"):
                        iface["subinterfaces"][0]["enabled_protocols"] += \
                            ["IGMP"]
            interfaces += [iface]
            snmp_ifindex += 1
        match = self.rx_ip.search(self.cli("show network"))
        ip_address = match.group("ip_address")
        ip_subnet = match.group("ip_subnet")
        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
        iface = {
            "name": "0/0",
            "type": "SVI",
            "admin_status": True,
            "oper_status": True,
            "enabled_protocols": [],
            "subinterfaces": [{
                "name": "0/0",
                "admin_status": True,
                "oper_status": True,
                "enabled_afi": ['IPv4'],
                "ipv4_addresses": [ip_address],
                "vlan_ids": [int(match.group("vlan_id"))]
            }]
        }
        if match.group("ipv6_address"):
            iface["subinterfaces"][0]["ipv6_addresses"] = \
            [match.group("ipv6_address")]
            iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
        if match.group("ip_address1") \
        and match.group("ip_address1") != "0.0.0.0":
            ip_address = match.group("ip_address1")
            ip_subnet = match.group("ip_subnet1")
            ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
            iface["subinterfaces"][0]["ipv4_addresses"] += [ip_address]
        if match.group("vlan_id1"):
            iface["subinterfaces"][0]["vlan_ids"] += \
                [int(match.group("vlan_id1"))]
        interfaces += [iface]
        return [{"interfaces": interfaces}]
