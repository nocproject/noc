# ----------------------------------------------------------------------
# ElectronR.KO01M.get_interfaces
# ----------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinterfaces import IGetInterfaces


class Script(BaseScript):
    name = "ElectronR.KO01M.get_interfaces"
    interface = IGetInterfaces

    def execute_snmp(self):
        return [
            {
                "interfaces": [
                    {
                        "type": "physical",
                        "name": "eth0",
                        "admin_status": True,
                        "oper_status": True,
                        "mac": self.snmp.get("1.3.6.1.4.1.35419.1.1.6.0"),
                        "snmp_ifindex": 100,
                        "hints": ["noc::interface::role::uplink"],
                        "subinterfaces": [],
                    }
                ]
            }
        ]
