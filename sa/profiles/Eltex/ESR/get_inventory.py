# ---------------------------------------------------------------------
# Eltex.ESR.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2023-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Eltex.ESR.get_inventory"
    interface = IGetInventory
    cache = True

    def execute_snmp(self, **kwargs):
        entity = self.scripts.get_version()
        res = []
        res += [
            {
                "type": "CHASSIS",
                "vendor": "Eltex",
                "part_no": entity["platform"],
                "serial": entity["caps"]["Chassis | Serial Number"],
                "revision": entity["caps"]["Chassis | HW Version"],
            }
        ]
        for r in res:
            if r["type"] == "CHASSIS" and self.has_snmp():
                r.update({"sensors": self.get_chassis_sensors()})
        return res

    def execute_cli(self, **kwargs):
        entity = self.scripts.get_version()
        res = []
        res += [
            {
                "type": "CHASSIS",
                "vendor": "Eltex",
                "part_no": entity["platform"],
                "serial": entity["caps"]["Chassis | Serial Number"],
                "revision": entity["caps"]["Chassis | HW Version"],
            }
        ]
        for r in res:
            if r["type"] == "CHASSIS" and self.has_snmp():
                r.update({"sensors": self.get_chassis_sensors()})
        return res

    def get_chassis_sensors(self):
        r = []
        # Fan state
        for i in [1, 2, 3, 4, 5]:
            for oid, v in self.snmp.getnext(f"1.3.6.1.4.1.89.53.15.1.{i+3}"):
                if v != 1:
                    v = 0
                r += [
                    {
                        "name": f"Fan-{i}",
                        "status": bool(v),
                        "description": f"State of Fan-{i}",
                        "measurement": "StatusEnum",
                        "labels": [
                            "noc::sensor::placement::internal",
                            "noc::sensor::mode::flag",
                            "noc::sensor::targer::fan",
                        ],
                        "snmp_oid": f"1.3.6.1.4.1.89.53.15.1.{i+3}",
                    }
                ]
        # Power Supply state
        for i in [1, 2]:
            for oid, v in self.snmp.getnext(f"1.3.6.1.4.1.89.53.15.1.{i+1}"):
                if v != 1:
                    v = 0
                r += [
                    {
                        "name": f"PS-{i}",
                        "status": bool(v),
                        "description": f"State of PS-{i}",
                        "measurement": "StatusEnum",
                        "labels": [
                            "noc::sensor::placement::internal",
                            "noc::sensor::mode::flag",
                            "noc::sensor::target::supply",
                        ],
                        "snmp_oid": f"1.3.6.1.4.1.89.53.15.1.{i+1}",
                    }
                ]
        return r
