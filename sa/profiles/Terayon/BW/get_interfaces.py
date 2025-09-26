# ---------------------------------------------------------------------
# Terayon.BW.get_interfaces
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
    name = "Terayon.BW.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_sh_int = re.compile(
        r"^(?P<interface>\d+\S*)\s+(?P<type>\S+)\s+(?P<mtu>\d+)\s+\d+\s+"
        r"(?P<mac>\S+)\s+(?P<oper_status>Up|Down)\s+(?P<admin_status>Up|Down)",
        re.MULTILINE,
    )
    rx_sub = re.compile(
        r"^(?P<interface>\d+\S*\.\d+)\s+VLAN\s+(?P<vlan_id>\d+)\s+(?P<mtu>\d+)\s*\n", re.MULTILINE
    )
    rx_ip = re.compile(
        r"^(?P<ip>\d\S+)\s+(?P<mask>\d+\S+)\s+(?:primary|secondary)\s+"
        r"(?P<interface>\d+\S*)\s*\n",
        re.MULTILINE,
    )

    def execute(self):
        interfaces = []
        v = self.cli("show interfaces", cached=True)
        for match in self.rx_sh_int.finditer(v):
            if match.group("type") in ["cableDownstream", "cableUpstream", "cableUsChannel"]:
                continue
            name = match.group("interface")
            mac = match.group("mac")
            mtu = match.group("mtu")
            a_stat = match.group("admin_status").lower() == "up"
            o_stat = match.group("oper_status").lower() == "up"
            iface = {
                "type": "physical",
                "name": name,
                "mac": mac,
                "admin_status": a_stat,
                "oper_status": o_stat,
                "mtu": mtu,
                "subinterfaces": [
                    {
                        "name": name,
                        "mac": mac,
                        "admin_status": a_stat,
                        "oper_status": o_stat,
                        "mtu": mtu,
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            interfaces += [iface]
        for match in self.rx_sub.finditer(v):
            ifname, vlan_id = match.group("interface").split(".")
            for i in interfaces:
                if i["name"] == ifname:
                    if i["subinterfaces"][0]["name"] == ifname:
                        i["subinterfaces"] = []
                    i["subinterfaces"] += [
                        {
                            "name": match.group("interface"),
                            "mtu": match.group("mtu"),
                            "enabled_afi": ["BRIDGE"],
                            "vlan_ids": [match.group("vlan_id")],
                        }
                    ]
                    break
        v = self.cli("show interfaces ip-brief")
        for match in self.rx_ip.finditer(v):
            ip = match.group("ip")
            mask = match.group("mask")
            ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(mask))
            if "." in match.group("interface"):
                ifname, vlan_id = match.group("interface").split(".")
            else:
                ifname = match.group("interface")
                vlan_id = 0
            for i in interfaces:
                if i["name"] == ifname:
                    if vlan_id == 0:
                        sub = i["subinterfaces"][0]
                        if "IPv4" not in sub["enabled_afi"]:
                            sub["enabled_afi"] += ["IPv4"]
                        if "ipv4_addresses" not in sub:
                            sub["ipv4_addresses"] = [ip_address]
                        else:
                            sub["ipv4_addresses"] += [ip_address]
                        break
                    for sub in i["subinterfaces"]:
                        if sub["name"] == match.group("interface"):
                            if "IPv4" not in sub["enabled_afi"]:
                                sub["enabled_afi"] += ["IPv4"]
                            if "ipv4_addresses" not in sub:
                                sub["ipv4_addresses"] = [ip_address]
                            else:
                                sub["ipv4_addresses"] += [ip_address]
                            break

        return [{"interfaces": interfaces}]
