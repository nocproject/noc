# ---------------------------------------------------------------------
# Alstec.24xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Alstec.24xx.get_inventory"
    interface = IGetInventory
    always_prefer = "S"
    port_map = {10: "1", 18: "2", 26: "3"}  # 16, 2  # 8, 2  # 24, 2

    def get_sensors(self):
        r = [
            # BB (black box module)
            {
                "name": "door",
                "status": True,
                "description": "Дверь",
                "measurement": "StatusEnum",
                "labels": ["noc::sensor::placement::door"],
                "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.5.7.0",
            },
            # temp1
            {
                "name": "temp",
                "status": True,
                "description": "Значение температуры с датчика",
                "measurement": "Celsius",
                "labels": ["noc::sensor::placement::external", "noc::sensor::mode::temperature"],
                "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.5.6.0",
            },
        ]
        # power supply module
        r += [
            # v230
            {
                "name": "psu_input",
                "status": True,
                "description": "Напряжени питания",
                "measurement": "Volt AC",
                "labels": ["noc::sensor::placement::psu", "noc::sensor::mode::voltage"],
                "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.3.6.0",
            },
            # temp1
            {
                "name": "psu_temp",
                "status": True,
                "description": "Температура блока питания",
                "measurement": "Celsius",
                "labels": ["noc::sensor::placement::psu", "noc::sensor::mode::temperature"],
                "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.3.8.0",
            },
        ]
        # PUM (control and monitoring module)
        # BP (battery pack module)
        v = None
        try:
            v = self.snmp.get("1.3.6.1.4.1.27142.1.2.45.1.4.9.0")
        except self.snmp.SNMPError:
            pass
        if v:
            r += [
                {
                    "name": "battery_charge_mode",
                    "status": True,
                    "description": "статус зарядки",
                    "measurement": "Current",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.7.0",
                },
                {
                    "name": "battery_charge_current",
                    "status": True,
                    "description": "Ток заряда батареи",
                    "measurement": "Current",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.8.0",
                },
                {
                    "name": "battery_charge_U",
                    "status": True,
                    "description": "Напряжение на батареях",
                    "measurement": "Volt DC",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.9.0",
                },
                {
                    "name": "battery_U1",
                    "status": True,
                    "description": "Напряжение на 1 батарее",
                    "measurement": "Volt DC",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.10.1.2.1",
                },
                {
                    "name": "battery_U2",
                    "status": True,
                    "description": "Напряжение на 2 батарее",
                    "measurement": "Volt DC",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.10.1.2.2",
                },
                {
                    "name": "battery_U3",
                    "status": True,
                    "description": "Напряжение на 3 батарее",
                    "measurement": "Volt DC",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.10.1.2.3",
                },
                {
                    "name": "battery_U4",
                    "status": True,
                    "description": "Напряжение на 4 батарее",
                    "measurement": "Volt DC",
                    "snmp_oid": "1.3.6.1.4.1.27142.1.2.45.1.4.10.1.2.4",
                },
            ]
        # GP (guard pack module)
        return r

    def execute_snmp(self, **kwargs):
        platform = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.3.0")
        serial = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.4.0")
        revision = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.14.0")
        port_num = self.snmp.get("1.3.6.1.2.1.2.1.0")
        if port_num in self.port_map:
            platform = "%s-0%s" % (platform, self.port_map[port_num])
        if not platform:
            raise NotImplementedError
        r = {
            "type": "CHASSIS",
            "vendor": "Alstec",
            "part_no": platform,
        }
        if serial and len(serial) > 5:
            r["serial"] = serial
        if revision:
            r["revision"] = revision
        if self.is_builtin_controller:
            sensors = self.get_sensors()
            if sensors:
                r["sensors"] = sensors
        return [r]
