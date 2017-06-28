# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
# python modules
import re
from collections import defaultdict
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    """
    """
    name = "InfiNet.WANFlexX.get_interfaces"
    interface = IGetInterfaces
    cache=True

    rx_ifname = re.compile(r"^(?P<name>\S+): \S+ mtu (?P<mtu>\d+)$",
                           re.MULTILINE)
    rx_mac = re.compile(r"^\s+ether (?P<mac>[0-9a-f:]+)\s?$",
                        re.MULTILINE)
    rx_vlan = re.compile(r"^\s+vlan: (?P<vlan>\d+)",
                         re.MULTILINE)
    rx_ipaddr = re.compile(r"^(?P<ifname>\S+)\s+(?P<net>[0-9\./]+)\s+"
                           r"(?P<ipaddr>[0-9\.]+)\s+",
                           re.MULTILINE)

    TYPE_MAP = {
        "lo": "loopback",
        "et": "physical",
        "rf": "physical",
        "vl": "SVI",
        "nu": "null"
    }

    def execute(self):
        # collect interfaces basic information
        ifaces = []
        cmd = self.cli("ifconfig -a")
        for block in cmd.split("\n\n"):
            match = self.rx_ifname.search(block)
            if not match:
                continue
            ifname = match.group("name")
            if ifname.startswith("svi"):  # tmp hack
                continue
            iface = {
                "name": ifname,
                "type": self.TYPE_MAP[ifname[:2]],
                "subinterfaces": [{
                    "name": ifname,
                    "mtu": match.group("mtu"),
                    "enabled_afi": []
                }]
            }
            # get interfaces mac addresses
            match = self.rx_mac.search(block)
            if match:
                mac = match.group("mac")
                iface["mac"] = mac
                iface["subinterfaces"][0]["mac"] = mac
            # get SVI interfaces vlans
            match = self.rx_vlan.search(block)
            if match:
                iface["subinterfaces"][0]["vlan_ids"] = [match.group("vlan")]

            ifaces += [iface]
        # collect interfaces ipv4 addresses
        ipv4_ifaces = defaultdict(list)
        cmd = self.cli("netstat -i")
        for match in self.rx_ipaddr.finditer(cmd):
            ipv4_ifaces[match.group("ifname")] += [
                match.group("ipaddr") + "/" + \
                match.group("net").split("/")[1]
            ]
        for iface in ifaces:
            if iface["name"] in ipv4_ifaces:
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
                iface["subinterfaces"][0]["ipv4_addresses"] = ipv4_ifaces[iface["name"]]

        return [{"interfaces": ifaces}]
