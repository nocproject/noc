# ---------------------------------------------------------------------
# Rotek.BT.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Rotek.BT.get_inventory"
    interface = IGetInventory

    def get_chassis_sensors_default(self):
        r = [
            # In
            {
                "name": "in",
                "status": True,
                "description": "Дверь",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::door",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.1.0",
            },
            # v230
            {
                "name": "v230_state",
                "status": True,
                "description": "Флаг наличия сетевого напряжения AC 230В",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::supply",
                ],
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
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::voltage",
                    "noc::sensor::target::power_load",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.3.0",
            },
            {
                "name": "ups_battery_U",
                "status": True,
                "description": "ИБП. Напряжение на АКБ",
                "measurement": "Volt AC",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::voltage",
                    "noc::sensor::target::power_cell",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.6.0",
            },
            {
                "name": "current_battery",
                "status": True,
                "description": "Ток заряда АКБ",
                "measurement": "Ampere",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::current",
                    "noc::sensor::target::power_cell",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.5.15.1.5.0",
            },
        ]
        return r

    def get_chassis_sensors_4250lsr(self):
        r = [
            # In
            {
                "name": "in",
                "status": True,
                "description": "Дверь",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::door",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.1.0",
            },
            # v230
            {
                "name": "v230_state",
                "status": True,
                "description": "Флаг наличия сетевого напряжения AC 230В",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::supply",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.9.0",
            },
        ]
        check = self.snmp.get("1.3.6.1.4.1.41752.911.10.1.10.0")
        if check:
            # temp1
            r += [
                {
                    "name": "temp_out",
                    "status": True,
                    "description": "Температура в шкафу",
                    "measurement": "Celsius",
                    "labels": [
                        "noc::sensor::placement::external",
                        "noc::sensor::mode::temperature",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.2.0",
                },
            ]
        r += [
            {
                "name": "current_load",
                "status": True,
                "description": "Ток потребления нагрузки",
                "measurement": "Ampere",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::voltage",
                    "noc::sensor::target::power_load",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.3.0",
            },
            {
                "name": "ups_battery_U",
                "status": True,
                "description": "ИБП. Напряжение на АКБ",
                "measurement": "Volt AC",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::voltage",
                    "noc::sensor::target::power_cell",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.6.0",
            },
            {
                "name": "current_battery",
                "status": True,
                "description": "Ток заряда АКБ",
                "measurement": "Ampere",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::current",
                    "noc::sensor::target::power_cell",
                ],
                "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.5.0",
            },
        ]
        v = self.snmp.get("1.3.6.1.4.1.41752.911.10.1.13.1.0")
        if v:
            # Energy calc
            if v:
                r += [
                    {
                        "name": "elmeter_U",
                        "status": bool(v),
                        "description": "Электросчётчик. Значение напряжения сети",
                        "measurement": "Volt AC",
                        "labels": [
                            "noc::sensor::placement::elmeter",
                            "noc::sensor::mode::voltage",
                            "noc::sensor::target::supply",
                        ],
                        "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.13.2.0",
                    },
                    {
                        "name": "elmeter_I",
                        "status": bool(v),
                        "description": "Электросчётчик. Значение потребляемого тока",
                        "measurement": "Ampere",
                        "labels": [
                            "noc::sensor::placement::elmeter",
                            "noc::sensor::mode::current",
                            "noc::sensor::target::power_load",
                        ],
                        "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.13.3.0",
                    },
                    {
                        "name": "elmeter_Pwr",
                        "status": bool(v),
                        "description": "Электросчётчик. Значение потребляемой мощности",
                        "measurement": "Watt",
                        "labels": [
                            "noc::sensor::placement::elmeter",
                            "noc::sensor::mode::watt",
                            "noc::sensor::target::power_load",
                        ],
                        "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.13.10.0",
                    },
                    {
                        "name": "elmeter_Freq",
                        "status": bool(v),
                        "description": "Электросчётчик. значение частоты сети",
                        "measurement": "Hertz",
                        "labels": [
                            "noc::sensor::placement::elmeter",
                            "noc::sensor::mode::freq",
                            "noc::sensor::target::power_load",
                        ],
                        "snmp_oid": "1.3.6.1.4.1.41752.911.10.1.13.9.0",
                    },
                ]
                for num in range(1, 5):
                    v = self.snmp.get(f"1.3.6.1.4.1.27514.102.0.{23 + 1}.0")
                    if v:
                        r += [
                            {
                                "name": f"elmeter_Tariff{num}",
                                "status": bool(v),
                                "description": f"Электросчётчик. Суммарное значение потреблённой мощности по тарифу {num}",
                                "measurement": "Kilowatt-hour",
                                "labels": [
                                    "noc::sensor::placement::elmeter",
                                    "noc::sensor::mode::counter",
                                    "noc::sensor::target::power_load",
                                ],
                                "snmp_oid": f"1.3.6.1.4.1.41752.911.10.1.13.{4 + num}.0",
                            }
                        ]
        return r

    def get_chassis_sensors(self):
        if self.is_4250lsr:
            return self.get_chassis_sensors_4250lsr()
        return self.get_chassis_sensors_default()
