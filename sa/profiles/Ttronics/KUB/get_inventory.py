# ---------------------------------------------------------------------
# Ttronics.KUB.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Ttronics.KUB.get_inventory"
    interface = IGetInventory

    nano_input_config_map = {
        0: {"type": "volt", "units": "Volt AC"},
        1: {"type": "in", "units": "enum"},
        2: {"type": "relay", "units": "enum"},
        3: {"type": "counter", "units": "Unknown"},
        4: {"type": "vibration", "units": "Unknown"},
    }

    def get_oid(self, p_type, num):
        # @todo Amper .1.3.6.1.4.1.51315.1.19.0
        if p_type == "volt":
            return f"1.3.6.1.4.1.51315.1.{9 + num}.0"
        elif p_type in {"in", "relay"}:
            return f"1.3.6.1.4.1.51315.1.{2 + num}.0"
        elif p_type == "counter":
            return "1.3.6.1.4.1.51315.1.8.0"
        elif p_type == "vibration":
            return "1.3.6.1.4.1.51315.1.2.0"
        return

    def get_nano_sensors(self):
        r = [
            # temp
            {
                "name": "temp",
                "status": 1,
                "description": "Значение температуры с внутреннего датчика",
                "measurement": "Celsius",
                "snmp_oid": "1.3.6.1.4.1.51315.1.1.0",
            },
            # Supply voltage
            {
                "name": "supply",
                "status": 1,
                "description": "Напряжение питания устройства",
                "measurement": "Volt AC",
                "snmp_oid": "1.3.6.1.4.1.51315.1.14.0",
            },
        ]
        # Universal input
        tok = self.snmp.get("1.3.6.1.4.1.51315.1.19.0")
        for num in range(1, 5):
            in_config = self.snmp.get(f"1.3.6.1.4.1.51315.1.{14 + num}.0")
            if in_config not in self.nano_input_config_map:
                self.logger.warning("Unknown type of port")
                continue
            elif num == 1 and in_config == 0 and tok < 32760:
                # kubTok =-32760-obryv datchika
                # kubTok =-32767-ne nasntroena formula
                # Current (tok) sensor connected
                r += [
                    {
                        "name": f'{self.nano_input_config_map[num]["type"]}{num}',
                        "status": True,
                        "description": f"Универсальных вход {num}",
                        "measurement": "Ampere",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.19.0",
                    }
                ]
                continue
            oid = self.get_oid(self.nano_input_config_map[num]["type"], num)
            r += [
                {
                    "name": f'{self.nano_input_config_map[num]["type"]}{num}',
                    "status": True,
                    "description": f"Универсальных вход {num}",
                    "measurement": self.nano_input_config_map[num]["units"],
                    "snmp_oid": oid,
                }
            ]
            # ElMeter
            v = self.snmp.get("1.3.6.1.4.1.51315.1.26.0")
            if v:
                r += [
                    {
                        "name": "elmeter_U",
                        "status": bool(v),
                        "description": "Электросчётчик. Значение напряжения сети",
                        "measurement": "Volt AC",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.21.0",
                    },
                    {
                        "name": "elmeter_I",
                        "status": bool(v),
                        "description": "Электросчётчик. Значение потребляемого тока",
                        "measurement": "Ampere",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.22.0",
                    },
                    {
                        "name": "elmeter_Tariff1",
                        "status": bool(v),
                        "description": "Электросчётчик. Суммарное значение потреблённой мощности по тарифу 1",
                        "measurement": "Kilowatt-hour",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.23.0",
                    },
                    {
                        "name": "elmeter_Tariff2",
                        "status": bool(v),
                        "description": "Электросчётчик. Суммарное значение потреблённой мощности по тарифу 2",
                        "measurement": "Kilowatt-hour",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.24.0",
                    },
                    {
                        "name": "elmeter_Tariff12",
                        "status": bool(v),
                        "description": "Электросчётчик. Суммарное значение потреблённой мощности",
                        "measurement": "Kilowatt-hour",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.25.0",
                    },
                ]
            # UPS Link
            v = self.snmp.get("1.3.6.1.4.1.51315.1.29.0")
            r += [
                {
                    "name": "ups_rs232",
                    "status": v != 0,
                    "description": "Флаг наличия связи с ИБП по порту RS-232",
                    "measurement": "enum",
                    "snmp_oid": "1.3.6.1.4.1.51315.1.29.0",
                },
            ]
            if v != 0:
                r += [
                    {
                        "name": "ups_state",
                        "status": bool(v),
                        "description": "ИБП. Текущее состояние ИБП",
                        "measurement": "enum",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.27.0",
                    },
                    {
                        "name": "ups_battery_state",
                        "status": bool(v),
                        "description": "ИБП. Текущее состояние батареи ИБП",
                        "measurement": "enum",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.38.0",
                    },
                    {
                        "name": "ups_bypass",
                        "status": bool(v),
                        "description": "ИБП. Текущий статус bypass",
                        "measurement": "enum",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.31.0",
                    },
                    {
                        "name": "ups_mode",
                        "status": bool(v),
                        "description": "ИБП. Текущий режим работы ИБП",
                        "measurement": "enum",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.32.0",
                    },
                    {
                        "name": "ups_in_U",
                        "status": bool(v),
                        "description": "ИБП. Входное напряжение.",
                        "measurement": "Volt AC",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.33.0",
                    },
                    {
                        "name": "ups_Freq",
                        "status": bool(v),
                        "description": "ИБП. Значение частоты сети",
                        "measurement": "Hertz",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.34.0",
                    },
                    {
                        "name": "ups_out_U",
                        "status": bool(v),
                        "description": "ИБП. Выходное напряжение.",
                        "measurement": "Volt AC",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.35.0",
                    },
                    {
                        "name": "ups_load_P",
                        "status": bool(v),
                        "description": "ИБП. Нагрузка ИБП в %.",
                        "measurement": "Rate",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.37.0",
                    },
                    {
                        "name": "ups_load_P",
                        "status": bool(v),
                        "description": "ИБП. Нагрузка ИБП в W.",
                        "measurement": "Watt",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.36.0",
                    },
                    {
                        "name": "ups_battery_U",
                        "status": bool(v),
                        "description": "ИБП. Напряжение  батареи  ИБП.",
                        "measurement": "Volt AC",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.40.0",
                    },
                    {
                        "name": "ups_battery_capasity",
                        "status": bool(v),
                        "description": "ИБП. Ёмкость батареи в %.",
                        "measurement": "Rate",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.41.0",
                    },
                    {
                        "name": "ups_battery_temp",
                        "status": bool(v),
                        "description": "ИБП. Температура батареи",
                        "measurement": "Celsius",
                        "snmp_oid": "1.3.6.1.4.1.51315.1.39.0",
                    },
                ]
        return r

    femto_input_config_map = {
        0: {"type": "in", "units": "enum"},
        1: {"type": "volt", "units": "Volt AC"},
        2: {"type": "counter", "units": "Unknown"},
        3: {"type": "vibration", "units": "Unknown"},
        4: {"type": "impedance", "units": "Unknown"},
        9: {"type": "ups", "units": "Unknown"},
    }

    def get_femto_sensors(self):
        """
        0 - Дискретный;
        1 - Измерение напряжения;
        2 - Счётчик импульсов,
        3 - Датчик вибрации (Импульсный);
        4 - Измерение сопротивления;
        9 - Сигнал ИБП (Батарея разряжена);
        :return:
        """
        r = [
            # temp
            {
                "name": "temp",
                "status": 1,
                "description": "Значение температуры с выносного датчика",
                "measurement": "Celsius",
                "snmp_oid": "1.3.6.1.3.55.1.2.1.0",
            },
        ]
        # Universal input
        for num in range(1, 7):
            in_config = self.snmp.get(f"1.3.6.1.3.55.1.3.1.2.{num - 1}")
            if in_config not in self.femto_input_config_map:
                self.logger.warning("Unknown type of port")
                continue
            oid = self.get_oid(self.femto_input_config_map[in_config]["type"], num)
            r += [
                {
                    "name": f'{self.femto_input_config_map[in_config]["type"]}{num}',
                    "status": True,
                    "description": f"Универсальных вход {num}",
                    "measurement": self.femto_input_config_map[in_config]["units"],
                    "snmp_oid": oid,
                }
            ]
        return r

    def get_chassis_sensors(self):
        if self.is_femto:
            return self.get_femto_sensors()
        else:
            return self.get_nano_sensors()

    def execute_snmp(self):
        r = self.get_inv_from_version()
        sensors = self.get_chassis_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r
