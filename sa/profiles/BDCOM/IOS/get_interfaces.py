# ---------------------------------------------------------------------
# BDCOM.IOS.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table


class Script(BaseScript):
    name = "BDCOM.IOS.get_interfaces"
    interface = IGetInterfaces

    rx_iface = re.compile(
        r"^(?P<ifname>\S+) is (?P<admin_status>up|down|administratively down), "
        r"line protocol is (?P<oper_status>up|down)\s*\n"
        r"(^\s+protocolstatus.+\n)?"
        r"^\s+Ifindex is (?P<snmp_ifindex>\d+).*\n"
        r"(^\s+Description: (?P<description>.+)\n)?"
        r"^\s+Hardware is (?P<iftype>\S+),"
        r"( [Aa]ddress is (?P<mac>\S+)\s*\(.+)?\s*\n"
        r"(^\s+Interface address is (?P<ip_address>\S+)\s*\n)?"
        r"^\s+MTU (?P<mtu>\d+).+\n",
        re.MULTILINE,
    )
    rx_iface_brief = re.compile(
        r"^(?P<ifname>\S+).+(?:up|down|shutdown)\s+(?P<vlan_id>\d+)", re.MULTILINE
    )
    iftype = {
        "100BASE-TX": "physical",
        "Giga-FX": "physical",
        "Giga-TX": "physical",
        "Giga-Combo-TX": "physical",
        "10Giga-FX": "physical",
        "10Giga-FX-SFP": "physical",
        "10G-BASE-DAC": "physical",
        "EtherSVI": "SVI",
        "Null": "null",
        "PortAggregator": "aggregated",
    }

    def execute(self):
        interfaces = []
        c = self.cli("show interface")
        for match in self.rx_iface.finditer(c):
            iface = {
                "name": match.group("ifname"),
                "type": self.iftype[match.group("iftype")],
                "admin_status": match.group("admin_status") == "up",
                "oper_status": match.group("oper_status") == "up",
                "enabled_protocols": [],
                "snmp_ifindex": int(match.group("snmp_ifindex")),
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": match.group("admin_status") == "up",
                        "oper_status": match.group("oper_status") == "up",
                        "mtu": int(match.group("mtu")),
                        "enabled_afi": [],
                    }
                ],
            }
            description = match.group("description")
            if description is not None:
                iface["description"] = description.strip()
                iface["subinterfaces"][0]["description"] = description.strip()
            if iface["type"] == "physical":
                iface["subinterfaces"][0]["enabled_afi"] += ["BRIDGE"]
            elif iface["type"] == "SVI":
                iface["subinterfaces"][0]["vlan_ids"] = [iface["name"][4:]]
            mac = match.group("mac")
            if mac is not None:
                iface["mac"] = mac
                iface["subinterfaces"][0]["mac"] = mac
            ip_address = match.group("ip_address")
            if ip_address is not None:
                iface["subinterfaces"][0]["ipv4_addresses"] = [ip_address]
                iface["subinterfaces"][0]["enabled_afi"] += ["IPv4"]
            interfaces += [iface]
        c = self.cli("show interface brief")
        for match in self.rx_iface_brief.finditer(c):
            ifname = self.profile.convert_interface_name(match.group("ifname"))
            for i in interfaces:
                if ifname == i["name"]:
                    i["subinterfaces"][0]["untagged_vlan"] = match.group("vlan_id")
                    break
        c = self.cli("show vlan")
        for r in parse_table(c, allow_wrap=True, n_row_delim=", "):
            if not r[3]:
                continue
            vlan_id = int(r[0])
            # ports = r[3].split(", ")
            for p in r[3].split(", "):
                p = self.profile.convert_interface_name(p)
                for i in interfaces:
                    if p == i["name"]:
                        if "tagged_vlans" in i["subinterfaces"][0]:
                            i["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                        else:
                            i["subinterfaces"][0]["tagged_vlans"] = [vlan_id]
                        break
        return [{"interfaces": interfaces}]
