# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Ericsson.MINI_LINK.get_interfaces
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


class Script(BaseScript):
    name = "Ericsson.MINI_LINK.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^Interface (?P<port>.+?)collisions \d+", re.MULTILINE | re.DOTALL)
    rx_iface = re.compile(
        r"^(?P<ifname>\S+)\s*\n"
        r"^\s+Hardware is (?P<hw>\S+)(, address is (?P<mac>\S+))?\s*\n"
        r"(^\s+Interface is unnumbered. Using IPv4 address of (?P<u_iface>\S+) \((?P<local_ip>\S+)\)\s*\n)?"
        r"(^\s+Remote address: (?P<remote_ip>\S+)/32\s*\n)?"
        r"^\s+index (?P<ifindex>\d+) metric \d+ mtu (?P<mtu>\d+).+\n"
        r"^\s+<(?P<flags>\S+)>\s*\n", re.MULTILINE)
    rx_ipv4_address = re.compile(
        r"^\s+inet (?P<ip_address>\d+\S+/\d+)", re.MULTILINE)

    def execute(self):
        interfaces = []
        v = self.cli_clean("show interface")
        for p in self.rx_port.finditer(v):
            match = self.rx_iface.search(p.group("port"))
            i = {
                "name": match.group("ifname"),
                "type": self.profile.INTERFACE_TYPES.get(match.group("hw")),
                "admin_status": "RUNNING" in match.group("flags"),
                "oper_status": "UP," in match.group("flags"),
                "enabled_protocols": [],
                "snmp_ifindex": int(match.group("ifindex")),
                "subinterfaces": [{
                    "name": match.group("ifname"),
                    "admin_status": "RUNNING" in match.group("flags"),
                    "oper_status": "UP," in match.group("flags"),
                    "mtu": int(match.group("mtu")),
                    "snmp_ifindex": int(match.group("ifindex")),
                    "enabled_afi": []
                }]
            }
            if match.group("mac"):
                i["mac"] = match.group("mac")
                i["subinterfaces"][0]["mac"] = match.group("mac")
            if match.group("u_iface"):
                i["subinterfaces"][0]["ip_unnumbered_subinterface"] = \
                    match.group("u_iface")
            if match.group("local_ip") and match.group("remote_ip"):
                i["subinterfaces"][0]["tunnel"] = {
                    "type": "PPP",
                    "local_address": match.group("local_ip"),
                    "remote_address": match.group("remote_ip")
                }
            for match in self.rx_ipv4_address.finditer(p.group("port")):
                if "IPv4" not in i["subinterfaces"][0]["enabled_afi"]:
                    i["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
                if "ipv4_addresses" not in i["subinterfaces"][0]:
                    i["subinterfaces"][0]["ipv4_addresses"] = []
                i["subinterfaces"][0]["ipv4_addresses"] += [
                    match.group("ip_address")
                ]
            interfaces += [i]
        return [{"interfaces": interfaces}]
