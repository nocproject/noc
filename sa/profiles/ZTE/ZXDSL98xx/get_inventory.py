# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_inventory"
    interface = IGetInventory

    SNMP_UNKNOWN_VALUE = -10000

    def get_chassis_sensors(self):
        r = []
        # zxAnEpmEnvCurrentTemp
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.3902.1015.320.2.3.2.1.2", bulk=False):
            if v == 2:  # INTEGER {unused(1),used(2)}
                _, key = oid.split(".3902.1015.320.2.3.2.1.2.")
                value = self.snmp.get(f"1.3.6.1.4.1.3902.1015.320.2.3.2.1.3.{key}", cached=True)
                if value != self.SNMP_UNKNOWN_VALUE:
                    metrics = {
                        "name": "epm_temp",
                        "status": True,
                        "description": "Температура",
                        "measurement": "Celsius",
                        "snmp_oid": f"1.3.6.1.4.1.3902.1015.320.2.3.2.1.3.{key}",
                    }
                    r += [metrics]
        # zxAnEpmEnvCurrentHumidity
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.3902.1015.320.2.3.6.1.2", bulk=False):
            if v == 2:  # INTEGER {unused(1),used(2)}
                _, key = oid.split(".3902.1015.320.2.3.6.1.2.")
                metrics = {
                    "name": "epm_humidity",
                    "status": True,
                    "description": "Влажность",
                    "measurement": "Percent",
                    "snmp_oid": f"1.3.6.1.4.1.3902.1015.320.2.3.6.1.3.{key}",
                }
                r += [metrics]
        # zxAnEpmEnvCurrentGuard #INTEGER {normal(1),abnormal(2)}
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.3902.1015.320.2.3.11.1.2", bulk=False):
            i = 1
            if v == 2:  # INTEGER {unused(1),used(2)
                _, key = oid.split(".3902.1015.320.2.3.11.1.2.")
                metrics = {
                    "name": f"epm_door{i}",
                    "status": True,
                    "description": f"Дверь {i}",
                    "measurement": "Scalar",
                    "snmp_oid": f"1.3.6.1.4.1.3902.1015.320.2.3.11.1.3.{key}",
                }
                i += 1
                r += [metrics]
        return r

    def execute_snmp(self):
        r = self.get_inv_from_version()
        sensors = self.get_chassis_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r

    def execute_cli(self):
        r = self.get_inv_from_version()
        sensors = self.get_chassis_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r
