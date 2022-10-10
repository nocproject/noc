# ----------------------------------------------------------------------
# Vector.Lambda.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_interfaces import Script as BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4
from noc.core.snmp.render import render_mac


class Script(BaseScript):
    name = "Vector.Lambda.get_interfaces"
    interface = IGetInterfaces

    rx_net = re.compile(
        r"MAC\s+addr\s+:\s+(?P<mac>\S+)\n"
        r"IP addr\s+:\s+(?P<ip>\S+)\n"
        r"Netmask\s+:\s+(?P<mask>\S+)\n",
        re.MULTILINE,
    )
    rx_port = re.compile(r"Receiver (?P<port>\S) power")

    def execute_snmp(self, **kwargs):
        ip = None
        interfaces = {
            "Output": {
                "name": "Output",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
            "Input A": {
                "name": "Input A",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
            "Input B": {
                "name": "Input B",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
        }
        if self.is_vectrar2d2:
            ips = self.snmp.get("1.3.6.1.4.1.17409.1.3.1.9.0")
            mac = self.snmp.get(
                "1.3.6.1.4.1.17409.1.3.2.1.1.1.0",
                display_hints={"1.3.6.1.4.1.17409.1.3.2.1.1.1.0": render_mac},
            )
            ip = ["%s/24" % ips]
        elif self.is_sysid_support:
            mac = self.snmp.get(
                "1.3.6.1.4.1.34652.2.11.5.1.0",
                display_hints={"1.3.6.1.4.1.34652.2.11.5.1.0": render_mac},
            )
        else:
            ips = self.snmp.get("1.3.6.1.4.1.5591.1.3.1.9.0")
            mac = self.snmp.get(
                "1.3.6.1.4.1.5591.1.3.2.7.0",
                display_hints={"1.3.6.1.4.1.5591.1.3.2.7.0": render_mac},
            )
            ip = ["%s/24" % ips]
        interfaces["mgmt"] = {
            "name": "mgmt",
            "admin_status": True,
            "oper_status": True,
            "type": "physical",
            "mac": mac,
            "hints": ["noc::interface::role::mgmt"],
            "subinterfaces": [
                {
                    "name": "mgmt",
                    "enabled_afi": ["IPv4"],
                    "mac": mac,
                    "ipv4_addresses": ip,
                    "admin_status": True,
                    "oper_status": True,
                }
            ],
        }
        return [{"interfaces": list(interfaces.values())}]

    def execute_cli(self, **kwargs):
        net = self.cli("net dump")
        match = self.rx_net.search(net)
        if match:
            ipaddr = match.group("ip")
            mask = match.group("mask")
            mac = match.group("mac")
            ip = IPv4(ipaddr, mask)
        else:
            raise self.NotSupportedError
        iface = [
            {
                "name": "mgmt",
                "admin_status": True,
                "oper_status": True,
                "type": "management",
                "mac": mac,
                "hints": ["noc::interface::role::mgmt"],
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "enabled_afi": ["IPv4"],
                        "mac": mac,
                        "ipv4_addresses": [ip],
                        "admin_status": True,
                        "oper_status": True,
                    }
                ],
            }
        ]

        dev = self.cli("dev dump")
        for match in self.rx_port.finditer(dev):
            iface += [
                {
                    "name": "Input %s" % match.group("port"),
                    "admin_status": True,
                    "oper_status": True,
                    "type": "physical",
                    "subinterfaces": [],
                }
            ]
        iface += [
            {
                "name": "Output",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            }
        ]

        return [{"interfaces": iface}]
