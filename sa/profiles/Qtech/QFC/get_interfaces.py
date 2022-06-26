# ----------------------------------------------------------------------
# Qtech.QFC.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "Qtech.QFC.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self):
        if self.is_lite:
            mac = self.snmp.get("1.3.6.1.4.1.27514.103.0.4.0")
        else:
            mac = self.snmp.get("1.3.6.1.4.1.27514.102.0.4.0")

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
