# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.5440.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
import re


class Script(BaseScript):
    name = "Alstec.5440.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>(?:br|eth|usb)\d+(?:\.\d+)?)\s+"
        r"Link encap:Ethernet\s+HWaddr (?P<mac>\S+)\s*\n"
        r"(^\s+inet addr:(?P<ip>\S+)\s+Bcast:\S+\s+Mask:(?P<mask>\S+)\s*\n)?"
        r"^\s+(?P<flags>.+)MTU:(?P<mtu>\d+)\s+Metric:\d+\s*\n",
        re.MULTILINE
    )

    def execute(self):
        interfaces = []
        for match in self.rx_iface.finditer(self.cli("ifconfig")):
            ifname = match.group("ifname")
            iface = {
                "name": ifname,
                "type": "physical",
                "admin_status": "RUNNING " in match.group("flags"),
                "oper_status": "UP " in match.group("flags"),
                "mac": match.group("mac"),
                "subinterfaces": []
            }
            sub = {
                "name": ifname,
                "admin_status": "RUNNING " in match.group("flags"),
                "oper_status": "UP " in match.group("flags"),
                "mtu": match.group("mtu"),
                "mac": match.group("mac"),
            }
            if match.group("ip"):
                ip = match.group("ip")
                mask = match.group("mask")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
                sub["enabled_afi"] = ["IPv4"]
                sub["ipv4_addresses"] = [ip_address]
            found = False
            if "." in ifname:
                i1, i2 = ifname.split(".")
                for i in interfaces:
                    if i["name"] == i1:
                        i["subinterfaces"] += [sub]
                        found = True
                        break
            if not found:
                iface["subinterfaces"] += [sub]
                interfaces += [iface]
        return [{"interfaces": interfaces}]
