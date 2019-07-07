# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.VRP3.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
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
    name = "Huawei.VRP3.get_interfaces"
    interface = IGetInterfaces

    rx_mac = re.compile(r"^\s*MAC address:\s+(?P<mac>\S+)")
    rx_ip = re.compile(
        r"^\s*IP address\s*:\s+(?P<ip>\S+)\s*\n" r"^\s*Subnet mask\s*:\s+(?P<mask>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_vlan = re.compile(r"^\s+Inband VLAN is\s+(?P<vlanid>\d+)")
    rx_pvc = re.compile(
        r"^\s*\d+\s+(?P<ifname>\S+\s+\d+/\d+/\d+)\s+(?P<vpi>\d+)\s+"
        r"(?P<vci>\d+)\s+LAN\s+0/0/(?P<vlan>\d+)(?:\(\S+\)|)\s+\S+\s+\S+\s+\d+\s+\d+\s*\n",
        re.MULTILINE,
    )

    rx_pvc2 = re.compile(
        r"\s+\d+\s+LAN\s+0/0/(?P<vlan>\d+)(?:\(\S+\)|)\s+\S+\s+\S+\s+"
        r"(?P<ifname>\S+\s+\d+/\d+/\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s.*\n",
        re.MULTILINE,
    )

    rx_pvc3 = re.compile(
        r"^\s*\d+\s+(?P<ifname>\S+\s+\d+\s+\d+\s+\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)"
        r"\s+LAN\s+0\s+0\s+(?P<vlan>\d+)\s+\S+\s+\S+\s+\d+\s+\d+\s*\n",
        re.MULTILINE,
    )

    rx_pvc4 = re.compile(
        r"\s+\d+\s+LAN\s+\d+\s+\d+\s+(?P<vlan>\d+)\s+\S+\s+\S+\s+"
        r"(?P<ifname>\S+\s+\d+\s+\d+\s+\d+)\s+(?P<vpi>\d+)\s+(?P<vci>\d+)\s.*\n",
        re.MULTILINE,
    )

    def execute(self):
        interfaces = []
        vlans = []
        for v in self.scripts.get_vlans():
            vlans += [v["vlan_id"]]
        iface = {
            "name": "FE:0/0/1",
            "type": "physical",
            "subinterfaces": [
                {"name": "FE:0/0/1", "enabled_afi": ["BRIDGE"], "tagged_vlans": vlans}
            ],
        }
        interfaces += [iface]
        iface = {
            "name": "FE:0/0/2",
            "type": "physical",
            "subinterfaces": [
                {"name": "FE:0/0/2", "enabled_afi": ["BRIDGE"], "tagged_vlans": vlans}
            ],
        }
        interfaces += [iface]
        with self.configure():
            c = self.cli("show pvc all")
            if self.rx_pvc.search(c):
                r = self.rx_pvc.finditer(c)
            elif self.rx_pvc2.search(c):
                r = self.rx_pvc2.finditer(c)
            elif self.rx_pvc3.search(c):
                r = self.rx_pvc3.finditer(c)
            else:
                r = self.rx_pvc4.finditer(c)
            for match in r:
                ifname = match.group("ifname")
                sub = {
                    "name": ifname,
                    "enabled_afi": ["BRIDGE", "ATM"],
                    "vpi": int(match.group("vpi")),
                    "vci": int(match.group("vci")),
                    "vlan_ids": int(match.group("vlan")),
                }
                found = False
                for i in interfaces:
                    if ifname == i["name"]:
                        i["subinterfaces"] += [sub]
                        found = True
                        break
                if not found:
                    iface = {"name": ifname, "type": "physical", "subinterfaces": [sub]}
                    interfaces += [iface]

        match = self.re_search(self.rx_mac, self.cli("show atmlan mac-address"))
        mac = match.group("mac")
        match = self.re_search(self.rx_ip, self.cli("show atmlan ip-address"))
        addr = match.group("ip")
        mask = match.group("mask")
        ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
        with self.configure():
            c = self.cli("show nms")
            match = self.rx_vlan.search(c)
            vlan = int(match.group("vlanid"))
        iface = {
            "name": "mgmt",
            "type": "SVI",
            "admin_status": True,  # always True, since inactive
            "oper_status": True,  # SVIs aren't shown at all
            "mac": mac,
            "subinterfaces": [
                {
                    "name": "mgmt",
                    "admin_status": True,
                    "oper_status": True,
                    "mac": mac,
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": [ip_address],
                    "vlan_ids": vlan,
                }
            ],
        }
        interfaces += [iface]
        return [{"interfaces": interfaces}]
