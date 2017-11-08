# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP3.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.ip import IPv4
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Huawei.VRP3.get_interfaces"
    interface = IGetInterfaces

    rx_mac = re.compile(r"^\s*MAC address:\s+(?P<mac>\S+)")
    rx_ip = re.compile(
        r"^\s*IP address\s*:\s+(?P<ip>\S+)\s*\n"
        r"^\s*Subnet mask\s*:\s+(?P<mask>\S+)\s*\n",
        re.MULTILINE)
    rx_vlan = re.compile(r"^\s+Inband VLAN is\s+(?P<vlanid>\d+)")
    rx_pvc = re.compile(
        r"^\s*\d+\s+ADL\s+0/(?P<ifname>\d+/\d+)\s+(?P<vpi>\d+)\s+"
        r"(?P<vci>\d+)\s+LAN\s+0/0/(?P<vlan>\d+)\s+\S+\s+\S+\s+\d+\s+\d+\s*\n",
        re.MULTILINE)

    def execute(self):
        interfaces = []
        vlans = []
        for v in self.scripts.get_vlans():
            vlans += [v["vlan_id"]]
        iface = {
            "name": "0/0",
            "type": "physical",
            "subinterfaces": [{
                "name": "0/0",
                "enabled_afi": ["BRIDGE"],
                "tagged_vlans": vlans
            }]
        }
        interfaces += [iface]
        with self.configure():
            for match in self.rx_pvc.finditer(self.cli("show pvc all")):
                ifname = match.group("ifname")
                sub = {
                    "name": ifname,
                    "enabled_afi": ["BRIDGE", "ATM"],
                    "vpi": int(match.group("vpi")),
                    "vci": int(match.group("vci")),
                    "vlan_ids": int(match.group("vlan"))
                }
                found = False
                for i in interfaces:
                    if ifname == i["name"]:
                        i["subinterfaces"] += [sub]
                        found = True
                        break
                if not found:
                    iface = {
                        "name": ifname,
                        "type": "physical",
                        "subinterfaces": [sub]
                    }
                    interfaces += [iface]
        match = self.re_search(self.rx_mac,
                               self.cli("show atmlan mac-address"))
        mac = match.group("mac")
        match = self.re_search(self.rx_ip,
                               self.cli("show atmlan ip-address"))
        addr = match.group("ip")
        mask = match.group("mask")
        ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
        with self.configure():
            c = self.cli("show nms")
            match = self.rx_vlan.search(c)
            vlan = int(match.group('vlanid'))
        iface = {
            "name": "mgmt",
            "type": "SVI",
            "admin_status": True,  # always True, since inactive
            "oper_status": True,  # SVIs aren't shown at all
            "mac": mac,
            "subinterfaces": [{
                "name": "mgmt",
                "admin_status": True,
                "oper_status": True,
                "mac": mac,
                "enabled_afi": ["IPv4"],
                "ipv4_addresses": [ip_address],
                "vlan_ids": vlan
            }]
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
