# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8100.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.text import parse_table


class Script(BaseScript):
    name = "AlliedTelesis.AT8100.get_interfaces"
    cache = True
    interface = IGetInterfaces

    rx_interface = re.compile(
        r"^Interface (?P<ifname>port\S+)\s*\n"
        r"^\s+Link is (?P<oper_status>\S+), administrative state is (?P<admin_status>\S+)\s*\n"
        r"^\s+Address is (?P<mac>\S+)\s*\n"
        r"^\s+Description: (?P<descr>.*)\s*\n"
        r"^\s+index (?P<snmp_ifindex>\d+) mtu (?P<mtu>\d+)\s*\n",
        re.MULTILINE,
    )
    rx_port_vlan = re.compile(r"(?P<ifname>port\d+\.\d+\.\d+)\((?P<type>u|t)\)")
    rx_ip = re.compile(
        r"^(?P<ifname>vlan\d+)\s+(?P<ip>\S+)\s+admin (?P<admin_status>up|down).+\n", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show interface")
        ifaces = []
        for match in self.rx_interface.finditer(v):
            i = {
                "name": match.group("ifname"),
                "type": "physical",
                "mac": match.group("mac"),
                "description": match.group("descr"),
                "admin_status": match.group("admin_status") == "UP",
                "oper_status": match.group("oper_status") == "UP",
                "snmp_ifindex": match.group("snmp_ifindex"),
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "mac": match.group("mac"),
                        "description": match.group("descr"),
                        "admin_status": match.group("admin_status") == "UP",
                        "oper_status": match.group("oper_status") == "UP",
                        "enabled_afi": ["BRIDGE"],
                        "mtu": match.group("mtu"),
                        "tagged_vlans": [],
                    }
                ],
            }
            ifaces += [i]

        v = self.cli("show vlan brief", cached=True)
        t = parse_table(v, allow_wrap=True)
        for i in t:
            vlan_id = int(i[0])
            for match in self.rx_port_vlan.finditer(i[4]):
                ifname = match.group("ifname")
                tagged = match.group("type") == "t"
                for iface in ifaces:
                    if iface["name"] == ifname:
                        if tagged:
                            iface["subinterfaces"][0]["tagged_vlans"] += [vlan_id]
                        else:
                            iface["subinterfaces"][0]["untagged_vlan"] = vlan_id
                        break

        v = self.cli("show ip interface")
        for match in self.rx_ip.finditer(v):
            i = {
                "name": match.group("ifname"),
                "type": "SVI",
                "admin_status": match.group("admin_status") == "up",
                "oper_status": True,
                "subinterfaces": [
                    {
                        "name": match.group("ifname"),
                        "admin_status": match.group("admin_status") == "up",
                        "oper_status": True,
                        "ipv4_addresses": [match.group("ip")],
                        "enabled_afi": ["IPv4"],
                    }
                ],
            }
            i["subinterfaces"][0]["vlan_ids"] = int(match.group("ifname")[4:])
            ifaces += [i]
        return [{"interfaces": ifaces}]
