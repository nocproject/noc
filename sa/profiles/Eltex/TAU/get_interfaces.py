# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.TAU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Eltex.TAU.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<ifname>\S+)\s+Link\sencap:(?P<itype>\S+)\s+"
        r"(?:HWaddr\s+(?P<mac>\S+)|Loopback)(:?\s+inet\s+addr:(?P<ip>\S+)\s+"
        r"(?:(|\S+\s+)Mask:(?P<mask>\S+))|\s+)\s+\S.+MTU:(?P<mtu>\S+)",
        re.MULTILINE | re.IGNORECASE,
    )

    INTERFACE_TYPES = {"local": "loopback", "ethernet": "physical"}  # Loopback

    @classmethod
    def get_interface_type(cls, name):
        c = cls.INTERFACE_TYPES.get(name.lower())
        return c

    def execute(self):
        interfaces = []
        with self.profile.shell(self):
            v = self.cli("ifconfig", cached=True)
            for line in v.split("\n\n"):
                match = self.rx_sh_int.search(line)
                if match:
                    ifname = match.group("ifname")
                    itype = match.group("itype")
                    iface = {
                        "type": self.get_interface_type(itype),
                        "name": ifname,
                        "admin_status": True,
                        "oper_status": True,
                        "subinterfaces": [
                            {
                                "name": ifname,
                                "mtu": match.group("mtu"),
                                "admin_status": True,
                                "oper_status": True,
                                "enabled_afi": ["BRIDGE"],
                            }
                        ],
                    }
                    if match.group("ip"):
                        ip_address = match.group("ip")
                        ip_subnet = match.group("mask")
                        ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                        ip_list = [ip_address]
                        enabled_afi = []
                        ip_interfaces = "ipv4_addresses"
                        enabled_afi += ["IPv4"]
                        iface["subinterfaces"][0]["enabled_afi"] = enabled_afi
                        iface["subinterfaces"][0][ip_interfaces] = ip_list
                    if match.group("mac"):
                        mac = match.group("mac")
                        iface["mac"] = mac
                    interfaces += [iface]
        return [{"interfaces": interfaces}]
