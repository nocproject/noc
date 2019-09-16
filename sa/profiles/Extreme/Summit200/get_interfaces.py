# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Extreme.Summit200.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.validators import is_int


class Script(BaseScript):
    name = "Extreme.Summit200.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^\s+(?P<port>\d+)\s+[PR] \S+(?P<admin_state>[ED]) (?P<oper_state>\S+)\s+", re.MULTILINE
    )
    rx_vlan = re.compile(
        r"with name \"(?P<vlan_name>\S+)\" created by .+\n"
        r"^\s+Tagging:\s+802.1Q Tag (?P<vlan_id>\d+)\s*\n"
        r"^\s+Priority:\s+802.1P Priority \d+\s*\n"
        r"(^\s+IP:\s+(?P<ip>\S+)/(?P<mask>\S+)\s*\n)?",
        re.MULTILINE,
    )
    rx_untagged = re.compile(r"^\s+Untag:(?P<untagged>.*)", re.MULTILINE | re.DOTALL)
    rx_tagged = re.compile(r"^\s+Tagged:(?P<tagged>.*)", re.MULTILINE | re.DOTALL)
    rx_ipfdb = re.compile(
        r"^(?P<ip>\S+)\s+.+\d+\s+(?P<mac>\S+)\s+(?P<vlan_id>\d+)\s+CPU", re.MULTILINE
    )

    def execute_cli(self):
        interfaces = []
        v = self.cli("show ports info")
        for match in self.rx_port.finditer(v):
            iface = {
                "name": match.group("port"),
                "type": "physical",
                "admin_status": match.group("admin_state") == "E",
                "oper_status": match.group("oper_state") == "active",
                "subinterfaces": [
                    {
                        "name": match.group("port"),
                        "admin_status": match.group("admin_state") == "E",
                        "oper_status": match.group("oper_state") == "active",
                        "enabled_afi": ["BRIDGE"],
                    }
                ],
            }
            interfaces += [iface]
        c = self.cli("show ipfdb")
        for v in self.cli("show vlan detail").split("VLAN Interface"):
            match = self.rx_vlan.search(v)
            if not match:
                continue
            vlan_id = int(match.group("vlan_id"))
            match1 = self.rx_untagged.search(v)
            if match1:
                untagged = match1.group("untagged").split()
                for ifname in untagged:
                    if ifname == "Tagged:":
                        break
                    if not is_int(ifname):
                        ifname = ifname[1:]
                    for i in interfaces:
                        if i["name"] == ifname:
                            i["subinterfaces"][0]["untagged_vlan"] = vlan_id
                            break
            match1 = self.rx_tagged.search(v)
            if match1:
                tagged = match1.group("tagged").split()
                for ifname in tagged:
                    if not is_int(ifname):
                        ifname = ifname[1:]
                    for i in interfaces:
                        if i["name"] == ifname:
                            if "tagged_vlans" in i["subinterfaces"][0]:
                                i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                            else:
                                i["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
                            break
            if match.group("ip"):
                ip = match.group("ip")
                ip_address = "%s/%s" % (ip, IPv4.netmask_to_len(match.group("mask")))
                iface = {
                    "name": match.group("vlan_name"),
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": True,
                    "subinterfaces": [
                        {
                            "name": match.group("vlan_name"),
                            "admin_status": True,
                            "oper_status": True,
                            "enabled_afi": ["IPv4"],
                            "ip_addresses": [ip_address],
                            "vlan_ids": vlan_id,
                        }
                    ],
                }
                for match1 in self.rx_ipfdb.finditer(c):
                    if match1.group("ip") == ip and int(match1.group("vlan_id")) == vlan_id:
                        iface["mac"] = match1.group("mac")
                        iface["subinterfaces"][0]["mac"] = match1.group("mac")
                        break
                interfaces += [iface]
        return [{"interfaces": interfaces}]
