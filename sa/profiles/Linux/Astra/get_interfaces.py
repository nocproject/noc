# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Linux.Astra.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
Important see: https://ru.wikipedia.org/w/index.php?oldid=75745192

"""
# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Linux.Astra.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifindex>\S+):\s+(?P<ifname>\S+):\s+\<(LOOPBACK|BROADCAST,MULTICAST)(,|)(?P<oper_status>UP|)(,\S+|)\>\s+mtu\s+(?P<mtu>\d+).*(?P<admin_status>UP|DOWN|UNKNOWN).*"
        r"\s+link\/(loopback|ether)\s+(?P<mac>\S+).*(?:"
        r"\s+inet\s+(?P<ip>\d+.\d+.\d+.\d+\/\d+)|)",
        re.MULTILINE,
    )

    rx_master = re.compile(
        r"\d+: (?P<name>\S+):\s<(?P<status>\S+)>\s[a-zA-Z0-9,<>_ ]+ master (?P<master>\S+)\s.*\n"
        r"    link\/ether (?P<mac>\S+) brd",
        re.IGNORECASE | re.DOTALL,
    )

    def execute_cli(self, interface=None):

        interfaces = []
        # Ethernet ports
        ifcfg = self.cli("ip a", cached=True)

        for match in self.rx_iface.finditer(ifcfg):
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
                "mac": match.group("mac") if match.group("mac") != "00:00:00:00:00:00" else None,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "mtu": match.group("mtu"),
                        "mac": match.group("mac")
                        if match.group("mac") != "00:00:00:00:00:00"
                        else None,
                        "admin_status": admin_status,
                        "oper_status": oper_status,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }

            if match.group("ip"):
                if IPv4(match.group("ip")):
                    iface["subinterfaces"][0]["ipv4_addresses"] = [match.group("ip")]
                    iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
            interfaces += [iface]
        return [{"interfaces": interfaces}]
