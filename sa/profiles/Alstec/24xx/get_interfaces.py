# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Alstec.24xx.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s*(?P<port>\d+/\d+|\d+/\d+/\d+)\s+(?P<admin_status>\S+)\s+\S+\s+(?P<oper_status>\S+)",
        re.MULTILINE,
    )
    rx_desc = re.compile(
        r"^\s*(?P<port>\d+/\d+|\d+/\d+/\d+)\s+(?:Enable|Disable)\s+(?:Up|Down)\s+(?P<desc>\S+)$",
        re.MULTILINE,
    )
    rx_vlan = re.compile(
        r"^interface (?P<port>\d+/\d+)\s*\n"
        r"(?:^no.+\n)*(^vlan pvid (?P<pvid>\d+)\s*$)?"
        r"^vlan participation include \S+\s*\n"
        r"(^vlan tagging (?P<tagged>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^\s*IP(?:v4)? Address\s*\.+ (?P<ip_address>\S+)\s*\n"
        r"^\s*Subnet Mask\s*\.+ (?P<ip_subnet>\S+)\s*\n"
        r"(^\s*(Additional )?IP Address\s*\.+ \S+\s*\n)?"
        r"(^\s*(Additional )?Subnet Mask\s*\.+ \S+\s*\n)?"
        r"(^\s*Default Gateway\s*\.+ \S+\s*\n)?"
        r"(^\s*DHCPv4 Mode\s*\.+ \S+\s*\n)?"
        r"(^\s*IPv6 Auto[Cc]onfig Mode\s*\.+ \S+\s*\n)?"
        r"(^\s*IPv6 Administrative Mode\s*\.+ \S+\s*\n)?"
        r"(^\s*IPv6 (address|Prefix is)\s*\.+ (?P<ipv6_address>\S+)\s*\n)?"
        r"(^\s*DHCPv6 Mode\s*\.+ \S+\s*\n)?"
        r"(^\s*IPv6 Link-Local Address\s*\.+ \S+\s*\n)?"
        r"^\s*(MAC Address|Burned In MAC Address)\s*\.+ (?P<mac>\S+)\s*\n"
        r"(^\s*Locally Administered MAC address\s*\.+ \S+\s*\n)?"
        r"(^\s*MAC Address Types?\s*\.+ .+\s*\n)?"
        r"(^\s*Configured IPv4 Protocols?\s*\.+ .+\s*\n)?"
        r"(^\s*Configured IPv6 Protocols?\s*\.+ .+\s*\n)?"
        r"(^\s*DHCPv6 Client DUID\s*\.+ .*\s*\n)?"
        r"(^\s*IPv6 AutoConfig Mode\s*\.+ .+\s*\n)?"
        r"^\s*Management VLAN ID\s*\.+ (?P<vlan_id>\d+)\s*\n",
        re.MULTILINE,
    )

    def execute_cli(self):
        sw = {
            sp["interface"]: {"tagged": sp["tagged"], "untagged": sp.get("untagged")}
            for sp in self.scripts.get_switchport()
        }
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
                "subinterfaces": [
                    {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "Enable",
                        "oper_status": match.group("oper_status") == "Up",
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            for matchd in self.rx_desc.finditer(d):
                if matchd.group("port") == ifname:
                    iface["description"] = matchd.group("desc")
                    iface["subinterfaces"][0]["description"] = matchd.group("desc")
            if ifname in sw:
                if sw[ifname]["tagged"]:
                    iface["subinterfaces"][0]["tagged_vlans"] = sw[ifname]["tagged"]
                if sw[ifname]["untagged"]:
                    iface["subinterfaces"][0]["untagged_vlan"] = sw[ifname]["untagged"]
            interfaces += [iface]
            snmp_ifindex += 1
        v = self.cli("show network", cached=True)
        match = self.rx_ip.search(v)
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
            "subinterfaces": [
                {
                    "name": "0/0",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": match.group("mac"),
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": [int(match.group("vlan_id"))],
                }
            ],
        }
        if match.group("ipv6_address"):
            iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
            iface["subinterfaces"][0]["ipv6_addresses"] = [match.group("ipv6_address")]
        interfaces += [iface]
        return [{"interfaces": interfaces}]
