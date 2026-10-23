# ----------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_interfaces"
    interface = IGetInterfaces
    cache = True

    def execute_snmp(self):
        mac = self.snmp.get("1.3.6.1.3.55.1.2.2.0")

        return [
            {
                "interfaces": [
                    {
                        "type": "physical",
                        "name": "eth0",
                        "admin_status": True,
                        "oper_status": True,
                        "mac": mac,
                        "snmp_ifindex": 100,
                        "hints": ["noc::interface::role::uplink"],
                        "subinterfaces": [],
                    }
                ]
            }
        ]
