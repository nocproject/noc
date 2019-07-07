# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Vector.Lambda.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


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
