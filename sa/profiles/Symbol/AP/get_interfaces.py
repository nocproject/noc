# ---------------------------------------------------------------------
# Symbol.AP.get_interfaces
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Symbol.AP.get_interfaces"
    interface = IGetInterfaces

    rx_brief = re.compile(
        r"^(?P<ifname>\S+)\s+(?P<oper_state>UP|DOWN)\s+(?P<mac>\S+)", re.MULTILINE
    )
    rx_ether = re.compile(
        r"^Interface (?P<ifname>\S+) is (?P<oper_state>UP|DOWN)\s*\n"
        r"^\s+Hardware-type: ethernet, Mode: Layer 2, Address: (?P<mac>\S+)\s*\n"
        r"^\s+Index: (?P<snmp_ifindex>\d+), Metric: \d+, MTU: (?P<mtu>\d+)",
        re.MULTILINE,
    )
    rx_ip = re.compile(r"^\s*ip address (?P<ip>\d\S+)", re.MULTILINE)

    def execute_cli(self):
        interfaces = []
        c = self.cli("show interface brief")
        for match in self.rx_brief.finditer(c):
            ifname = match.group("ifname")
            v = self.cli("show interface %s" % ifname)
            if ifname.startswith("ge"):
                match1 = self.rx_ether.search(v)
                iface = {
                    "name": ifname,
                    "type": "physical",
                    "admin_status": True,
                    "oper_status": match.group("oper_status") == "UP",
                    "mac": match.group("mac"),
                    "snmp_ifindex": int(match1.group("snmp_ifindex")),
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": True,
                            "oper_status": match.group("oper_status") == "UP",
                            "mac": match.group("mac"),
                            "mtu": int(match1.group("mtu")),
                            "enabled_afi": ["BRIDGE"],
                        }
                    ],
                }
                interfaces += [iface]
            if ifname.startswith("vlan"):
                iface = {
                    "name": ifname,
                    "type": "SVI",
                    "admin_status": True,
                    "oper_status": match.group("oper_status") == "UP",
                    "mac": match.group("mac"),
                    "subinterfaces": [
                        {
                            "name": ifname,
                            "admin_status": True,
                            "oper_status": match.group("oper_status") == "UP",
                            "mac": match.group("mac"),
                            "vlan_ids": ifname[4:],
                        }
                    ],
                }
                match1 = self.rx_ip.search(v)
                if match1:
                    iface["subinterface"][0]["IPv4"]
                    iface["subinterface"][0]["ipv4_addresses"] = match1.group("ip")
                interfaces += [iface]

        return [{"interfaces": interfaces}]
