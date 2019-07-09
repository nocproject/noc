# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# IRE-Polus.Taros.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces
from noc.core.ip import IPv4


class Script(BaseScript):
    name = "IRE-Polus.Taros.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self, **kwargs):
        if self.is_EAU:
            addr = self.snmp.get("1.3.6.1.4.1.35702.2.2.0")
            mask = self.snmp.get("1.3.6.1.4.1.35702.2.3.0")
        elif self.is_BS:
            addr = self.snmp.get("1.3.6.1.4.1.14546.3.8.1.1.13.5.0")
            mask = self.snmp.get("1.3.6.1.4.1.14546.3.8.1.1.13.6.0")
        ip = IPv4(addr, mask)
        iface = [
            {
                "name": "mgmt",
                "admin_status": True,
                "oper_status": True,
                "type": "management",
                "subinterfaces": [
                    {
                        "name": "mgmt",
                        "enabled_afi": ["IPv4"],
                        "ipv4_addresses": [ip],
                        "admin_status": True,
                        "oper_status": True,
                    }
                ],
            }
        ]
        # Optical ports
        iface += [
            {
                "name": "Input 1",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
            {
                "name": "Input 2",
                "admin_status": True,
                "oper_status": True,
                "type": "physical",
                "subinterfaces": [],
            },
        ]

        return [{"interfaces": iface}]
