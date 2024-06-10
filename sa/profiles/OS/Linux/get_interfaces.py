# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OS.Linux.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "OS.Linux.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifindex>\S+):\s+(?P<ifname>\S+):\s+\<(LOOPBACK|BROADCAST,MULTICAST)(,|)(?P<oper_status>UP|)(,\S+|)\>\s+mtu\s+(?P<mtu>\d+).*(?P<admin_status>UP|DOWN|UNKNOWN).*"
        r"\s+link\/(loopback|ether)\s+(?P<mac>\S+)",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"inet\s+(?P<ip>\d+.\d+.\d+.\d+\/\d+) (brd \S+ |)scope (host|global) (secondary |)(?P<iface>\S+)",
        re.MULTILINE,
    )

    def execute_cli(self, interface=None):

        interfaces = []
        # Ethernet ports
        ifaces = list(
            filter(None, self.cli("ls -A /sys/class/net", cached=True).strip().split(" "))
        )
        for i in ifaces:
            ipdev = self.cli(f"ip addr show dev {i}", cached=True)
            print(ipdev)
            match = self.rx_iface.search(ipdev)
            ipmatch = self.rx_ip.search(ipdev)
            admin_status = True
            if match.group("admin_status") == "DOWN":
                admin_status = False
            oper_status = False
            if match.group("oper_status"):
                oper_status = True
            iface = {
                "name": match.group("ifname"),
                "ifindex": match.group("ifindex"),
                "type": self.profile.get_interface_type(match.group("ifname")),
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [],
            }
            if ipmatch:
                add = False
                for ip in self.rx_ip.finditer(ipdev):
                    if IPv4(ip.group("ip")):
                        for ii in iface["subinterfaces"]:
                            if ii["name"] == ip.group("iface"):
                                ii["ipv4_addresses"] += [ip.group("ip")]
                                add = True
                        if add:
                            add = False
                            continue
                        iface["subinterfaces"] += [
                            {
                                "name": ip.group("iface"),
                                "mtu": match.group("mtu"),
                                "mac": (
                                    match.group("mac")
                                    if match.group("mac") != "00:00:00:00:00:00"
                                    else None
                                ),
                                "admin_status": admin_status,
                                "oper_status": oper_status,
                                "enabled_afi": ["BRIDGE", "IPv4"],
                                "ipv4_addresses": [ip.group("ip")],
                            }
                        ]
            else:
                iface["subinterfaces"] = [
                    {
                        "name": match.group("ifname"),
                        "mtu": match.group("mtu"),
                        "mac": (
                            match.group("mac")
                            if match.group("mac") != "00:00:00:00:00:00"
                            else None
                        ),
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                    }
                ]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
