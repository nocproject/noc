# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# OneAccess.TDRE.get_interfaces
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
    name = "OneAccess.TDRE.get_interfaces"
    interface = IGetInterfaces

    rx_ip_iface = re.compile(
        r"^\s+ifDescr = (?P<descr>.+)\n"
        r"^\s+ifType = (?P<iftype>\S+)\s*\n"
        r"^\s+ifOperStatus = (?P<oper_status>\S+)\s*\n"
        r"^\s+ifLastChange = .+\n"
        r"^\s+address = (?P<ip_address>\S+)\s*\n"
        r"^\s+mask = (?P<ip_mask>\S+)\s*\n"
        r"^\s+secondaryIp =\s*"
        r"^\s+{\s*"
        r"(^\s+.+\n)?"
        r"^\s+}\s*",
        re.MULTILINE
    )

    IF_TYPES = {
        "softwareLoopback": "loopback",
        "ethernet-csmacd": "SVI"
    }

    def execute(self):
        interfaces = []
        self.cli("SELGRP Status")
        c = self.cli("GET ip/router/interfaces[]/")
        for match in self.rx_ip_iface.finditer(c):
            ip = match.group("ip_address")
            mask = IPv4.netmask_to_len(match.group("ip_mask"))
            iface = {
                "name": match.group("descr"),
                # "admin_status": True,
                "oper_status": match.group("oper_status") == "up",
                "type": self.IF_TYPES[match.group("iftype")],
                "description": match.group("descr"),
                "subinterfaces": [{
                    "name": match.group("descr"),
                    # "admin_status": True,
                    "oper_status": match.group("oper_status") == "up",
                    "description": match.group("descr"),
                    "enabled_afi": ["IPv4"],
                    "ipv4_addresses": ["%s/%s" % (ip, mask)]
                }]
            }
            interfaces += [iface]
        return [{"interfaces": interfaces}]
