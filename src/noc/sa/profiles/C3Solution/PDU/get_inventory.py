# ---------------------------------------------------------------------
# C3Solution.PDU.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2026 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "C3Solution.PDU.get_inventory"
    interface = IGetInventory

    def get_chassis_sensors(self):
        r = []
        for phase in [1, 2, 3]:
            num = phase + 2
            r += [
                {
                    "name": f"PhaseBalance{phase}",
                    "status": True,
                    "description": f"Баланс фазы {phase}",
                    "measurement": "%",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.30966.6.1.1.{num}.2.0",
                },
                {
                    "name": f"PhaseRealPower{phase}",
                    "status": True,
                    "description": f"Потребляемая мощность на фазе {phase}",
                    "measurement": "W",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.30966.6.1.1.{num}.3.0",
                    # .1.3.6.1.4.1.30966.8.1.2.1.1.0
                },
                {
                    "name": f"PhaseCurrent{phase}",
                    "status": True,
                    "description": f"Потребляемый ток на фазе {phase}",
                    "measurement": "A",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.30966.6.1.1.{num}.4.0",
                },
                {
                    "name": f"PhaseVoltage{phase}",
                    "status": True,
                    "description": f"Напряжение на фазе {phase}",
                    "measurement": "VAC",
                    # "labels": self.femto_input_config_map[in_config]["labels"],
                    "snmp_oid": f"1.3.6.1.4.1.30966.6.1.1.{num}.5.0",
                },
            ]
        return r

    def execute_snmp(self, **kwargs):
        # productModelNumber
        platform = self.snmp.get("1.3.6.1.4.1.30966.6.1.1.2.0")
        part_no = f"RPDU={platform.strip()}"
        sensors = self.get_chassis_sensors()
        return [
            {
                "type": "CHASSIS",
                "vendor": "Vertiv",
                "part_no": [part_no],
                # "serial": serial,
                # "revision": revision,
                "sensors": sensors,
            }
        ]
