# ----------------------------------------------------------------------
# Ttronics.KUB.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2020 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Ttronics.KUB.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self):
        mac = self.snmp.get("1.3.6.1.4.1.51315.1.20.0")
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
                        "subinterfaces": [],
                    }
                ]
            }
        ]
