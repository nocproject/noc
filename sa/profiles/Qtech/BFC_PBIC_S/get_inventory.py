# ---------------------------------------------------------------------
# Qtech.BFC_PBIC_S.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2021 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Qtech.BFC_PBIC_S.get_inventory"
    interface = IGetInventory

    femto_input_config_map = {
        0: {"type": "in", "units": "StatusEnum"},
        1: {"type": "volt", "units": "Volt AC"},
        2: {"type": "counter", "units": "Scalar"},
        3: {"type": "vibration", "units": "Scalar"},
        4: {"type": "impedance", "units": "Scalar"},
        9: {"type": "ups", "units": "Scalar"},
    }

    def get_sensors(self):
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
                "name": "temp_out",
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
            # oid = self.get_oid(self.femto_input_config_map[in_config]["type"], num)
            oid = f"1.3.6.1.3.55.1.3.1.4.{num - 1}"
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

    def execute_snmp(self):
        r = self.get_inv_from_version()
        sensors = self.get_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r
