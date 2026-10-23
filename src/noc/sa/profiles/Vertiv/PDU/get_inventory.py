# ---------------------------------------------------------------------
# Vertiv.PDU.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Vertiv.PDU.get_inventory"
    interface = IGetInventory

    def get_chassis_sensors(self):
        r = []
        for phase in [1, 2, 3]:
            r += [
                {
                    "name": f"PhaseBalance{phase}",
                    "status": True,
                    "description": f"Баланс фазы {phase}",
                    "measurement": "%",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.21239.5.2.3.2.1.17.{phase}",
                },
                {
                    "name": f"PhaseRealPower{phase}",
                    "status": True,
                    "description": f"Потребляемая мощность на фазе {phase}",
                    "measurement": "W",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.21239.5.2.3.2.1.12.{phase}",
                },
                {
                    "name": f"PhaseCurrent{phase}",
                    "status": True,
                    "description": f"Потребляемый ток на фазе {phase}",
                    "measurement": "A",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.21239.5.2.3.2.1.8.{phase}",
                },
                {
                    "name": f"PhaseVoltage{phase}",
                    "status": True,
                    "description": f"Напряжение на фазе {phase}",
                    "measurement": "VAC",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.21239.5.2.3.2.1.4.{phase}",
                },
            ]
        return r

    def execute_snmp(self, **kwargs):
        # productModelNumber
        part_no = self.snmp.get("1.3.6.1.4.1.21239.5.2.1.8.0")
        serial = self.snmp.get("1.3.6.1.4.1.21239.5.2.1.10.0")
        revision = self.snmp.get("1.3.6.1.4.1.21239.5.2.1.9.0")
        sensors = self.get_chassis_sensors()
        return [
            {
                "type": "CHASSIS",
                "vendor": "Vertiv",
                "part_no": [part_no],
                "serial": serial,
                "revision": revision,
                "sensors": sensors,
            }
        ]
