# ---------------------------------------------------------------------
# Iskratel.VOIP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Iskratel.VOIP.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>\S+?\d+) information:\s*\n^\s*(?P<flags>.+)\n", re.MULTILINE
    )
    rx_mac = re.compile(r"^\s*MAC address (?P<mac>\S+)", re.MULTILINE)
    rx_vlan = re.compile(r"^\s*VLAN ID\s+(?P<vlan_id>\d+)", re.MULTILINE)
    rx_ip = re.compile(
        r"^\s*IP address (?P<ip>\S+) \(primary\), mask (?P<mask>\S+\d+)?", re.MULTILINE
    )

    def execute(self):
        interfaces = []
        for iface in self.cli("show interface").split("Network device "):
            match = self.rx_iface.search(iface)
            if not match:
                continue
            ifname = match.group("ifname")
            admin_status = "Up" in match.group("flags")
            oper_status = "Running" in match.group("flags")
            if "Loopback" in match.group("flags"):
                iftype = "loopback"
            else:
                iftype = "SVI"
            i = {
                "name": ifname,
                "type": iftype,
                "admin_status": admin_status,
                "oper_status": oper_status,
                "subinterfaces": [
                    {"name": ifname, "admin_status": admin_status, "oper_status": oper_status}
                ],
            }
            match = self.rx_mac.search(iface)
            if match:
                i["mac"] = match.group("mac")
                i["subinterfaces"][0]["mac"] = match.group("mac")
            match = self.rx_vlan.search(iface)
            if match:
                i["subinterfaces"][0]["vlan_ids"] = match.group("vlan_id")
            match = self.rx_ip.search(iface)
            if match:
                ip_address = match.group("ip")
                ip_subnet = match.group("mask")
                ip_address = "%s/%s" % (ip_address, IPv4.netmask_to_len(ip_subnet))
                i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                i["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
            interfaces += [i]
        return [{"interfaces": interfaces}]
