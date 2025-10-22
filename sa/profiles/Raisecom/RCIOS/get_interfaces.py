# ----------------------------------------------------------------------
# Raisecom.RCIOS.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4, IPv6


class Script(BaseScript):
    name = "Raisecom.RCIOS.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"Interface\s+(?P<iface>\S+)\s+is\s+(?P<oper>up|down),\s+"
        r"Admin\s+status\s+is\s+(?P<admin>up|down)\s*\n"
        r"^\s+aliasname\s+\S+\s*\n"
        r"(^\s+inet addr:\s+(?P<ip_addr>\S+)\s+(Bcast:\s+\d+\S+\d+\s+)?"
        r"Mask:\s*(?P<ip_mask>\d+\S+\d+)\s*\n)?"
        r"(^\s+inet addr6:\s+(?P<ipv6_addr>\S+)\s+Mask:\s*(?P<ipv6_mask>\S+)\s*\n)?"
        r"(^\s+Hardware address:\s+(?P<mac>\S+)\s*\n)?"
        r"(^\s+.+?\s+MTU:\s*(?P<mtu>\d+).+?\n)?"
        r"(^.+?\n)?"
        r"(^.+?\n)?"
        r"(^\s+Forwarding mode is SWITCH_ACCESS, pvid is (?P<pvid>\d+), mirror \S+"
        r", loopback-detect (?P<ctp_state>\S+),.+\n)?",
        re.MULTILINE,
    )
    rx_conf_iface = re.compile(
        r"^interface (?P<iface>\S+)\s*\n((?P<cfg>.*?)\n)?^!\s*\n", re.MULTILINE | re.DOTALL
    )
    rx_trunk = re.compile(r"switchport trunk permit vlan (?P<vlan_id>\d+)")

    def execute(self):
        conf_interfaces = {}
        interfaces = []
        v = self.cli("show running-config interface", cached=True)
        for match in self.rx_conf_iface.finditer(v):
            conf_interfaces[match.group("iface")] = match.group("cfg")
        v = self.cli("show interface", cached=True)
        for match in self.rx_iface.finditer(v):
            ifname = match.group("iface")
            iface = {
                "name": ifname,
                "type": self.profile.get_interface_type(ifname),
                "oper_status": match.group("oper") == "up",
                "admin_status": match.group("admin") == "up",
                "subinterfaces": [
                    {
                        "name": ifname,
                        "oper_status": match.group("oper") == "up",
                        "admin_status": match.group("admin") == "up",
                        "enabled_afi": [],
                    }
                ],
            }
            if match.group("mac"):
                iface["mac"] = match.group("mac")
                iface["subinterfaces"][0]["mac"] = match.group("mac")
            if match.group("mtu"):
                iface["subinterfaces"][0]["mtu"] = int(match.group("mtu"))
            if match.group("ip_addr"):
                ip = match.group("ip_addr")
                netmask = str(IPv4.netmask_to_len(match.group("ip_mask")))
                ip = ip + "/" + netmask
                ip_list = [ip]
                iface["subinterfaces"][0]["ipv4_addresses"] = ip_list
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
            if match.group("ipv6_addr"):
                ip = match.group("ipv6_addr")
                netmask = match.group("ipv6_mask")
                ip = IPv6(ip, netmask=match.group("ipv6_mask")).prefix
                ip_list = [ip]
                iface["subinterfaces"][0]["ipv6_addresses"] = ip_list
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv6"]
            else:
                iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            if match.group("pvid"):
                iface["subinterfaces"][0]["untagged_vlan"] = int(match.group("pvid"))
            if conf_interfaces.get(ifname):
                cfg = conf_interfaces[ifname]
                for match in self.rx_trunk.finditer(cfg):
                    if iface["subinterfaces"][0].get("tagged_vlans"):
                        iface["subinterfaces"][0]["tagged_vlans"] += [int(match.group("vlan_id"))]
                    else:
                        iface["subinterfaces"][0]["tagged_vlans"] = [int(match.group("vlan_id"))]
            interfaces += [iface]

        return [{"interfaces": interfaces}]
