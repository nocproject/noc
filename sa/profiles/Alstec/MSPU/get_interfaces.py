# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.MSPU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.ip import IPv4
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Alstec.MSPU.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>\S+\d+)\s+Link encap:Ethernet\s+HWaddr (?P<mac>\S+)",
        re.MULTILINE)
    rx_flags = re.compile(
        r"^\s+(?P<flags>.+)\s+MTU:(?P<mtu>\d+)\s+Metric:\d+",
        re.MULTILINE)
    rx_ip = re.compile(
        r"^\s+inet addr:(?P<ip>\S+)\s+Bcast:\S+\s+ Mask:(?P<mask>\S+)",
        re.MULTILINE)

    def execute(self):
        interfaces = []
        for l in self.cli("context ip router ifconfig").split("\n\n"):
            match = self.rx_iface.search(l)
            if not match:
                continue
            ifname = match.group("ifname")
            mac = match.group("mac")
            match = self.rx_flags.search(l)
            oper_status = "RUNNING" in match.group("flags")
            admin_status = "UP " in match.group("flags")
            mtu = match.group("mtu")
            if ifname.startswith("brv"):
                iftype = "physical"  # Must be IRB
            if ifname.startswith("hbr"):
                iftype = "physical"  # Must be IRB
            iftype = "physical"
            iface = {
                "name": ifname,
                "type": iftype,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "mac": mac,
                "mtu": mtu
            }
            match = self.rx_ip.search(l)
            if match:
                ip_address = match.group("ip")
                ip_subnet = match.group("mask")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                sub["ipv4_addresses"] = [ip_address]
                sub["enabled_afi"] = ['IPv4']
            found = False
            if "." in ifname:
                parent, vlan = ifname.split(".")
                sub["vlan_ids"] = [vlan]
                for i in interfaces:
                    if i["name"] == parent:
                        i["subinterfaces"] += [sub]
                        found = True
                        break
                continue
            iface["subinterfaces"] += [sub]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
