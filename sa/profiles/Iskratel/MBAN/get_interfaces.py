# ---------------------------------------------------------------------
# Iskratel.MBAN.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "Iskratel.MBAN.get_interfaces"
    interface = IGetInterfaces

    rx_port = re.compile(
        r"^(?P<port>\S+?\d+)\:?(?P<vpi>\d+)?\_?(?P<vci>\d+)?\s+"
        r"(?P<admin_status>Yes|No)\s+(?P<oper_status>Yes|No)\s+",
        re.MULTILINE,
    )
    rx_ip = re.compile(
        r"^(?P<port>\S+?\d+) - addrs (?P<ip>\S+) \[mask (?P<mask>\S+)\]\s+"
        r"\[broadcast \S+\]\s*\n\s+ether (?P<mac>\S+)\s*\n",
        re.MULTILINE,
    )

    rx_vlan = re.compile(
        r"^\s*(?P<vlan_id>\d+)\s+(?P<port>\S+?\d+)\s+keep\s+ingr\+egr\s*\n", re.MULTILINE
    )
    rx_vlan1 = re.compile(
        r"^(?P<port>\S+)\s+(?P<vlan_id>\d+)\s+untagged\s+(?P<mode>trunk|access)\s+",
        re.MULTILINE,
    )

    def execute(self):
        interfaces = []
        v = self.cli("show interface")
        iface_procc = set()
        sub_map = {}
        for match in self.rx_port.finditer(v):
            ifname = match.group("port")
            if ifname not in iface_procc:
                i = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": match.group("admin_status") == "Yes",
                    "oper_status": match.group("oper_status") == "Yes",
                    "subinterfaces": [],
                }
                iface_procc.add(ifname)
            elif match.group("vpi") and match.group("vci"):
                vpi = match.group("vpi")
                vci = match.group("vci")
                for ii in interfaces:
                    if ii["name"] == ifname:
                        ii["subinterfaces"] += [
                            {
                                "name": "%s:%s_%s" % (ifname, vpi, vci),
                                "admin_status": match.group("admin_status") == "Yes",
                                "oper_status": match.group("oper_status") == "Yes",
                                "enabled_afi": ["BRIDGE", "ATM"],
                                "vpi": vpi,
                                "vci": vci,
                            }
                        ]
                        sub_map["%s:%s_%s" % (ifname, vpi, vci)] = ii["subinterfaces"][-1]
                continue
            if match.group("vpi") and match.group("vci"):
                vpi = match.group("vpi")
                vci = match.group("vci")
                i["subinterfaces"] += [
                    {
                        "name": "%s:%s_%s" % (ifname, vpi, vci),
                        "admin_status": match.group("admin_status") == "Yes",
                        "oper_status": match.group("oper_status") == "Yes",
                        "enabled_afi": ["BRIDGE", "ATM"],
                        "vpi": vpi,
                        "vci": vci,
                    }
                ]
                sub_map["%s:%s_%s" % (ifname, vpi, vci)] = i["subinterfaces"][-1]
            else:
                i["subinterfaces"] += [
                    {
                        "name": ifname,
                        "admin_status": match.group("admin_status") == "Yes",
                        "oper_status": match.group("oper_status") == "Yes",
                        "enabled_afi": ["BRIDGE"],
                    }
                ]
                sub_map[ifname] = i["subinterfaces"][-1]

            interfaces += [i]
        for match in self.rx_ip.finditer(v):
            ifname = match.group("port")
            for i in interfaces:
                if i["name"] == ifname:
                    addr = match.group("ip")
                    mask = match.group("mask")
                    ip_address = "%s/%s" % (addr, IPv4.netmask_to_len(mask))
                    i["type"] = "SVI"
                    i["mac"] = match.group("mac")
                    i["subinterfaces"][0]["mac"] = match.group("mac")
                    i["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                    i["subinterfaces"][0]["enabled_afi"] = ["IPv4"]
        v = self.cli("show vlan detail")
        for match in self.rx_vlan.finditer(v):
            ifname = match.group("port")
            # for i in interfaces:
            #    if i['subinterfaces'][0]["name"] == ifname:
            if ifname in sub_map:
                if "tagged" in sub_map[ifname]:
                    sub_map[ifname]["tagged"] += [match.group("vlan_id")]
                else:
                    sub_map[ifname]["tagged"] = [match.group("vlan_id")]
        for match in self.rx_vlan1.finditer(v):
            ifname = match.group("port")
            # for i in interfaces:
            #    if i['subinterfaces'][0]["name"] == ifname:
            if ifname in sub_map:
                if match.group("mode") == "trunk":
                    sub_map[ifname]["untagged"] = match.group("vlan_id")
                else:
                    sub_map[ifname]["vlan_ids"] = [match.group("vlan_id")]
        return [{"interfaces": interfaces}]
