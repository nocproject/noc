# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "DLink.DAS.get_interfaces"
    interface = IGetInterfaces
    rx_eth = re.compile(
        r"^Interface\s+: (?P<name>\S+)\s*\n"
        r"^Type.+\n"
        r"^IP Address\s+: (?P<ip>\S+)\s+Mask\s+: (?P<mask>\S+)\s*\n"
        r"^Pkt Type.+\n"
        r"^Orl\(mbps\).+\n"
        r"^Configured Duplex.+\n"
        r"^Configured Speed.+\n"
        r"^Profile Name.+\n"
        r"^Mgmt VLAN Index\s+: (?P<vlan_id>\S+)\s*\n",
        re.MULTILINE
    )
    rx_stats = re.compile(
        r"^Interface\s+: (?P<name>\S+)\s+Description\s+: (?P<descr>.*)\n"
        r"^Type\s+: (?P<type>\S+)\s+Mtu\s+: (?P<mtu>\d+)\s*\n"
        r"^Bandwidth\s+: \d+\s+Phy Adddr\s+: (?P<mac>\S+)\s*\n"
        r"^Last Change\(sec\).+\n"
        r"^Admin Status\s+: (?P<admin_status>\S+)\s+Operational Status : (?P<oper_status>\S+)\s*\n",
        re.MULTILINE
    )
    IF_TYPES = {
        "ETHERNET": "physical",
        "EOA": "unknown",
        "Adsl": "physical",
        "Interleaved": "unknown",
        "AAL5": "unknown",
        "Fast": "unknown",
        "ATM": "physical",
    }
    def execute(self):
        interfaces = []
        #v = self.cli("get ethernet intf")
        v = self.cli("get interface stats")
        for match in self.rx_stats.finditer(v):
            i = {
                "name": match.group("name"),
                "type": self.IF_TYPES[match.group("type")],
                "admin_status": match.group("admin_status") == "Up",
                "oper_status": match.group("oper_status") == "Up",
                "enabled_protocols": [],
                "subinterfaces": [{
                    "name": match.group("name"),
                    "admin_status": match.group("admin_status") == "Up",
                    "oper_status": match.group("oper_status") == "Up",
                    # "ifindex": 1,
                    "enabled_afi": ['BRIDGE']
                }]
            }
            if match.group("mtu") != "0":
                i["subinterfaces"][0]["mtu"] = match.group("mtu")
            if match.group("mac") != "00:00:00:00:00:00":
                i["mac"] = match.group("mac")
                i["subinterfaces"][0]["mac"] = match.group("mac")
            if match.group("descr").strip() != "":
                descr = match.group("descr").strip()
                i["description"] = descr
                i["subinterfaces"][0]["description"] = descr
            if match.group("type") == "ATM":
                i["subinterfaces"][0]["enabled_afi"] += ["ATM"]
            if match.group("type") == "ETHERNET":
                i["subinterfaces"][0]["enabled_afi"] = []
            interfaces += [i]
        v = self.cli("get ethernet intf")
        for match in self.rx_eth.finditer(v):
            ifname = match.group("name")
            ip = match.group("ip")
            mask = match.group("mask")
            if ip == "0.0.0.0":
                continue
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            for i in interfaces:
                if i["name"] == ifname:
                    i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                    i["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
                    if match.group("vlan_id") != "-":
                        i["subinterfaces"][0]["vlan_ids"] = [match.group("vlan_id")]
                    break

        return [{"interfaces": interfaces}]
