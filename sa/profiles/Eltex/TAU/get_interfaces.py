# ---------------------------------------------------------------------
# Eltex.TAU.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_vlan


class Script(BaseScript):
    name = "Eltex.TAU.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<ifname>\S+)\s+Link\sencap:(?P<itype>\S+)\s+(?:HWaddr\s+(?P<mac>\S+)|Loopback)\s*\n"
        r"^(?:\s+inet\s+addr:\s*(?P<ip>\S+)\s+(?:(|\S+\s+)Mask:(?P<mask>\S+))\s*\n)?"
        r"^(?:\s+inet6\s+addr:\s*(?P<ip6>\S+)\s+Scope:\S+\s*\n)?"
        r"^\s+\S.+MTU:(?P<mtu>\S+)",
        re.MULTILINE | re.IGNORECASE,
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("ifconfig", cached=True)
        for line in v.split("\n\n"):
            match = self.rx_sh_int.search(line)
            if match:
                ifname = match.group("ifname")
                sub = {
                    "name": ifname,
                    "mtu": match.group("mtu"),
                    "admin_status": True,
                    "oper_status": True,
                    "enabled_afi": ["BRIDGE"],
                }
                if match.group("ip"):
                    ip_address = match.group("ip")
                    ip_subnet = match.group("mask")
                    ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                    sub["enabled_afi"] += ["IPv4"]
                    sub["ipv4_addresses"] = [ip_address]
                if match.group("ip6"):
                    ip6_address = match.group("ip6")
                    sub["enabled_afi"] += ["IPv6"]
                    sub["ipv6_addresses"] = [ip6_address]
                if "." in ifname:
                    parent, vlan = ifname.split(".")
                    if is_vlan(vlan):
                        sub["vlan_ids"] = int(vlan)
                    found = False
                    for i in interfaces:
                        if i["name"] == parent:
                            i["subinterfaces"] += [sub]
                            found = True
                            break
                    if found:
                        continue
                iface = {
                    "type": self.profile.get_interface_type(ifname),
                    "name": ifname,
                    "mtu": match.group("mtu"),
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [],
                }
                if match.group("mac"):
                    mac = match.group("mac")
                    iface["mac"] = mac
                iface["subinterfaces"] = [sub]
                interfaces += [iface]
        return [{"interfaces": interfaces}]
