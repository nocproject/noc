# ---------------------------------------------------------------------
# Qtech.QFC.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Qtech.QFC.get_inventory"
    interface = IGetInventory

    def get_v2_rev_sensors(self):
        r = []
        # @todo Old version merge to one OID
        # Optron input for 1 to 4
        for i in range(1, 5):
            r += [
                {
                    "name": f"in{i}",
                    "status": 1,
                    "description": f"Цифровой вход номер {i}",
                    "measurement": "StatusEnum",
                    "labels": ["noc::sensor::placement::external"],
                    "snmp_oid": f"1.3.6.1.4.1.27514.102.0.{4 + i}.0",
                }
            ]
        # Relay output
        for i in range(1, 3):
            r += [
                {
                    "name": f"relay{i}",
                    "status": 1,
                    "description": f"Реле {i}",
                    "measurement": "StatusEnum",
                    "labels": ["noc::sensor::placement::external", "noc::sensor::mode::relay"],
                    "snmp_oid": f"1.3.6.1.4.1.27514.102.0.{8 + i}.0",
                }
            ]
        r += [
            # V48 - Supply voltage
            {
                "name": "v48_supply",
                "status": 1,
                "description": "Напряжение питания устройства",
                "measurement": "Volt AC",
                "labels": [
                    "noc::sensor::placement::internal",
                    "noc::sensor::mode::voltage",
                    "noc::sensor::target::supply",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.11.0",
            },
            # V230 state
            {
                "name": "v230_state",
                "status": 1,
                "description": "Флаг наличия сетевого напряжения AC 230В",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::supply",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.12.0",
            },
            # tempIN
            {
                "name": "temp_in",
                "status": 1,
                "description": "Значение температуры с внутреннего датчика",
                "measurement": "Celsius",
                "labels": [
                    "noc::sensor::placement::internal",
                    "noc::sensor::mode::temperature",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.13.0",
            },
        ]
        # tempOut
        v = self.snmp.get("1.3.6.1.4.1.27514.102.0.14.0")
        r += [
            {
                "name": "temp_out",
                "status": bool(v),
                "description": "Значение температуры с внешнего датчика",
                "measurement": "Celsius",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::temperature",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.14.0",
            }
        ]
        v = self.snmp.get("1.3.6.1.4.1.27514.102.0.15.0")
        # Charging supply
        r += [
            {
                "name": "current_load",
                "status": bool(v),
                "description": "Ток потребления нагрузки",
                "measurement": "Ampere",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::current",
                    "noc::sensor::target::power_load",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.15.0",
            },
            {
                "name": "current_battery",
                "status": bool(v),
                "description": "Ток заряда АКБ",
                "measurement": "Ampere",
                "labels": [
                    "noc::sensor::placement::ups",
                    "noc::sensor::mode::current",
                    "noc::sensor::target::power_cell",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.102.0.16.0",
            },
        ]
        # ElMeter
        v = self.snmp.get("1.3.6.1.4.1.27514.102.0.20.0")
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
                    "snmp_oid": "1.3.6.1.4.1.27514.102.0.20.0",
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
                    "snmp_oid": "1.3.6.1.4.1.27514.102.0.21.0",
                },
                {
                    "name": "elmeter_Pwr",
                    "status": bool(v),
                    "description": "Электросчётчик. Значение потребляемой мощности",
                    "measurement": "Watt",
                    "snmp_oid": "1.3.6.1.4.1.27514.102.0.22.0",
                },
                {
                    "name": "elmeter_Freq",
                    "status": bool(v),
                    "description": "Электросчётчик. значение частоты сети",
                    "measurement": "Hertz",
                    "snmp_oid": "1.3.6.1.4.1.27514.102.0.23.0",
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
                            "snmp_oid": f"1.3.6.1.4.1.27514.102.0.{23 + 1}.0",
                        }
                    ]
        return r

    def get_v3_rev_sensors(self):
        r = [
            # In
            {
                "name": "in",
                "status": True,
                "description": "Цифровой вход",
                "measurement": "StatusEnum",
                "labels": [
                    "noc::sensor::placement::external",
                    "noc::sensor::mode::flag",
                    "noc::sensor::target::door",
                ],
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.5.0",
            },
            # Relay
            {
                "name": "relay",
                "status": True,
                "description": "Реле",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::relay"],
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.6.0",
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
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.7.0",
            },
            # temp1
            {
                "name": "temp1",
                "status": True,
                "description": "Значение температуры с датчика №1",
                "measurement": "Celsius",
                "labels": ["noc::sensor::placement::internal", "noc::sensor::mode::temperature"],
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.8.0",
            },
        ]
        # temp2
        v = self.snmp.get("1.3.6.1.4.1.27514.103.0.9.0")
        r += [
            {
                "name": "temp2",
                "status": bool(v),
                "description": "Значение температуры с датчика №2",
                "measurement": "Celsius",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::temperature"],
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.9.0",
            }
        ]
        # UPS Link
        v = self.snmp.get("1.3.6.1.4.1.27514.103.0.13.0")
        r += [
            {
                "name": "ups_rs232",
                "status": True,
                "description": "Флаг наличия связи с ИБП по порту RS-232",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::internal", "noc::sensor::mode::flag"],
                "snmp_oid": "1.3.6.1.4.1.27514.103.0.13.0",
            },
        ]
        if v:
            r += [
                {
                    "name": "ups_state",
                    "status": bool(v),
                    "description": "ИБП. Текущее состояние ИБП",
                    "measurement": "StatusEnum",
                    "labels": ["noc::sensor::placement::ups", "noc::sensor::mode::flag"],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.14.0",
                },
                {
                    "name": "ups_battery_state",
                    "status": bool(v),
                    "description": "ИБП. Текущее состояние батареи ИБП",
                    "measurement": "StatusEnum",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::flag",
                        "noc::sensor::target::power_cell",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.15.0",
                },
                {
                    "name": "ups_bypass",
                    "status": bool(v),
                    "description": "ИБП. Текущий статус bypass",
                    "measurement": "StatusEnum",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::flag",
                        "noc::sensor::target::bypass",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.16.0",
                },
                {
                    "name": "ups_mode",
                    "status": bool(v),
                    "description": "ИБП. Текущий режим работы ИБП",
                    "measurement": "StatusEnum",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::target::supply",
                        "noc::sensor::mode::flag",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.18.0",
                },
                {
                    "name": "ups_in_U",
                    "status": bool(v),
                    "description": "ИБП. Входное напряжение.",
                    "measurement": "Volt AC",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::voltage",
                        "noc::sensor::target::supply",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.19.0",
                },
                {
                    "name": "ups_Freq",
                    "status": bool(v),
                    "description": "ИБП. Значение частоты сети",
                    "measurement": "Hertz",
                    "labels": ["noc::sensor::placement::ups", "noc::sensor::target::supply"],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.23.0",
                },
                {
                    "name": "ups_out_U",
                    "status": bool(v),
                    "description": "ИБП. Выходное напряжение.",
                    "measurement": "Volt AC",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::voltage",
                        "noc::sensor::target::power_load",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.21.0",
                },
                {
                    "name": "ups_load_P",
                    "status": bool(v),
                    "description": "ИБП. Нагрузка ИБП в %.",
                    "measurement": "Percent",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::target::power_load",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.22.0",
                },
                {
                    "name": "ups_load_W",
                    "status": bool(v),
                    "description": "ИБП. Нагрузка ИБП в W.",
                    "measurement": "Watt",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::target::power_load",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.23.0",
                },
                {
                    "name": "ups_battery_U",
                    "status": bool(v),
                    "description": "ИБП. Напряжение  батареи  ИБП.",
                    "measurement": "Volt AC",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::voltage",
                        "noc::sensor::target::power_cell",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.24.0",
                },
                {
                    "name": "ups_battery_state_of_charge",
                    "status": bool(v),
                    "description": "ИБП. Ёмкость батареи в %.",
                    "measurement": "Percent",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::soc",
                        "noc::sensor::target::power_cell",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.25.0",
                },
                {
                    "name": "ups_battery_temp",
                    "status": bool(v),
                    "description": "ИБП. Температура батареи",
                    "measurement": "Celsius",
                    "labels": [
                        "noc::sensor::placement::ups",
                        "noc::sensor::mode::temperature",
                        "noc::sensor::target::power_cell",
                    ],
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.26.0",
                },
            ]
        # ElMeterLink
        v = self.snmp.get("1.3.6.1.4.1.27514.103.0.27.0")
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
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.27.0",
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
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.28.0",
                },
                {
                    "name": "elmeter_Pwr",
                    "status": bool(v),
                    "description": "Электросчётчик. Значение потребляемой мощности",
                    "labels": [
                        "noc::sensor::placement::elmeter",
                        "noc::sensor::mode::watt",
                        "noc::sensor::target::power_load",
                    ],
                    "measurement": "Watt",
                    "snmp_oid": "1.3.6.1.4.1.27514.103.0.29.0",
                },
            ]
            for num in range(1, 5):
                v = self.snmp.get(f"1.3.6.1.4.1.27514.103.0.{29 + num}.0")
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
                            "snmp_oid": f"1.3.6.1.4.1.27514.103.0.{29 + num}.0",
                        }
                    ]
        return r

    def get_chassis_sensors(self):
        # RS-485 elmeter  ElmeterCaps
        # RS-232 UPS - UPS Connected
        if not self.is_lite:
            return self.get_v2_rev_sensors()
        return self.get_v3_rev_sensors()
