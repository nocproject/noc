# ---------------------------------------------------------------------
# Generic.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python Modules
from typing import Dict, List

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Generic.get_inventory"
    interface = IGetInventory

    def get_sensor_labels(self) -> Dict[str, List[str]]:
        """
        For customizing. Return map sensor_name -> label.
        For sensor classification
        :return:
        """
        return {}

    def get_chassis_sensors(self):
        """
        Return sensors on device chassis
        :return:
        """
        return []

    def get_inv_from_version(self):
        v = self.scripts.get_version()
        serial = self.capabilities.get("Chassis | Serial Number")
        revision = self.capabilities.get("Chassis | HW Version")
        return [
            {
                "type": "CHASSIS",
                "vendor": v["vendor"],
                "part_no": [v["platform"]],
                "serial": serial,
                "revision": revision,
            }
        ]

    def processed_inventory(self):
        chassis = self.get_inv_from_version()
        sensors = self.get_chassis_sensors()
        if not sensors or not chassis:
            return chassis
        chassis[0]["sensors"] = sensors
        sensor_labels = self.get_sensor_labels()
        if not sensor_labels:
            return chassis
        for ss in sensors:
            if ss["name"] in sensor_labels and "labels" in ss:
                ss["labels"] = ss["labels"][:] + sensor_labels[ss["name"]]
            elif ss["name"] in sensor_labels and "labels" not in ss:
                ss["labels"] = sensor_labels[ss["name"]]
        return chassis

    def execute_snmp(self):
        return self.processed_inventory()

    def execute_cli(self):
        return self.processed_inventory()
