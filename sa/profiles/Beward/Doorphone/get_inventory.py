# ---------------------------------------------------------------------
# Beward.Doorphone.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Beward.Doorphone.get_inventory"
    interface = IGetInventory
    # always_prefer = "S"

    def get_sensors(self) -> list:
        """
        Returns sensors for execute_snmp function

        :return: list[dict] sensors
        """

        door_sensor_map = {
            1: "Door_1_sensor",
            2: "Door_2_sensor",
            3: "Main_sensor",
        }

        other_sensors_map = {
            3: "hacking_sensor",
            4: "reader_sensor",
            5: "video_module_sensor",
            6: "microcontroller_sensor",
        }

        result = []
        for i in range(1, 4):
            oid = f"1.3.6.1.4.1.44490.1.5.2.{i}.0"
            value = (
                False if self.snmp.get(oid) in (2, 3) else True
            )  # 1 - "open", 2 - "close", 3 - "break"
            name = door_sensor_map.get(int(oid.split(".")[-2]))
            sensor = {
                "name": name,
                "status": value,
                "description": f"{name} status",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::internal", "noc::sensor::mode::flag"],
                "snmp_oid": oid,
            }
            result.append(sensor)

        for index, name in other_sensors_map.items():
            oid = f"1.3.6.1.4.1.44490.1.6.{index}.0"
            value = False if self.snmp.get(oid) == 2 else True  # 1 - "ok", 2 - "break"
            sensor = {
                "name": name,
                "status": value,
                "description": f"{name} status",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::internal", "noc::sensor::mode::flag"],
                "snmp_oid": oid,
            }
            result.append(sensor)

        return result

    def execute_snmp(self, **kwargs):
        platform = self.version["platform"]
        result = {"type": "CHASSIS", "vendor": "Beward", "part_no": platform}
        sensors = self.get_sensors()
        if sensors:
            result["sensors"] = sensors
        return [result]
