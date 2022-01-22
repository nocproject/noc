# ---------------------------------------------------------------------
# Rotek.BT.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Rotek.BT.get_inventory"
    interface = IGetInventory

    def get_chassis_sensors(self):
        r = [
            # In
            {
                "name": "in",
                "status": True,
                "description": "Дверь",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::external"],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.1.0",
            },
            # v230
            {
                "name": "v230_state",
                "status": True,
                "description": "Флаг наличия сетевого напряжения AC 230В",
                "measurement": "StatusEnum",
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.9.0",
            },
            # temp1
            {
                "name": "temp_out",
                "status": True,
                "description": "Температура в шкафу",
                "measurement": "Celsius",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::temperature"],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.2.0",
            },
        ]
        r += [
            {
                "name": "current_load",
                "status": True,
                "description": "Ток потребления нагрузки",
                "measurement": "Ampere",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::current"],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.3.0",
            },
            {
                "name": "ups_battery_U",
                "status": True,
                "description": "ИБП. Напряжение на АКБ",
                "measurement": "Volt AC",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::voltage"],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.6.0",
            },
            {
                "name": "current_battery",
                "status": True,
                "description": "Ток заряда АКБ",
                "measurement": "Ampere",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::current"],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.5.0",
            },
        ]
        return r

    def execute_snmp(self):
        r = self.get_inv_from_version()
        sensors = self.get_chassis_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r
