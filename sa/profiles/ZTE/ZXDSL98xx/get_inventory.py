# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2022 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

import re

# NOC modules
from noc.sa.profiles.Generic.get_inventory import Script as BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_inventory"
    interface = IGetInventory

    SNMP_UNKNOWN_VALUE = -10000

    type = {
        "SCCV": "MAINBOARD",
        "SCCF": "MAINBOARD",
        "SCCE": "MAINBOARD",
        "ASTDB": "LINECARD",
        "ATLDZ": "LINECARD",
        "VSTGJ": "LINECARD",
        "PWAV": "PWR",
        "OGSDD": "SUBSLOT",
        "VOPCE": "SUBSLOT",
    }
    rx_card = re.compile(
        r"\s+(?P<slot>\d+)\s+(?P<cfgtype>\S+)\s+(?P<port>\d+)\s+"
        r"(?P<hardver>V?\S+|)\s+(?P<softver>V\S+|)\s+(?P<status>Inservice|Offline)\s+"
        r"(?P<serial>\S+)"
    )

    rx_subcard = re.compile(
        r"(?P<shelf>\d+)\s+(?P<slot>\d+)\s+(?P<cfgtype>\S+)\s+"
        r"(?P<hardver>V?\S+|)\s+(?P<softver>V\S+|)?\s+(?P<status>Inservice|Offline)"
    )

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

    def fill_ports(self):
        r = []
        v = self.cli("show card")
        for line in v.splitlines():
            match = self.rx_card.search(line)
            if match:
                r += [match.groupdict()]
        return r

    def execute_cli(self):
        r = self.get_inv_from_version()
        ports = self.fill_ports()
        for p in ports:
            i = {
                "type": self.type[p["cfgtype"]],
                "number": p["slot"],
                "vendor": "ZTE",
                "part_no": p["cfgtype"],
                "revision": p["hardver"],
                "serial": p["serial"],
            }
            r += [i]
            if "SCC" in p["cfgtype"]:
                subs = self.cli("show sub-card")
                for line in subs.splitlines():
                    match = self.rx_subcard.search(line)
                    if match:
                        sub = {
                            "type": self.type[match.group("cfgtype")],
                            "number": match.group("slot"),
                            "vendor": "ZTE",
                            "part_no": match.group("cfgtype"),
                            "revision": match.group("hardver"),
                        }
                        r += [sub]

        sensors = self.get_chassis_sensors()
        if sensors:
            r[0]["sensors"] = sensors
        return r
