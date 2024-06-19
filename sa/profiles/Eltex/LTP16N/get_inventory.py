# ---------------------------------------------------------------------
# Eltex.LTP16N.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2024-2024 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Eltex.LTP16N.get_inventory"
    interface = IGetInventory
    cache = True

    rx_platform = re.compile(
        r"^\s*([Tt][Yy][Pp][Ee]|Device\s+name):\s+(?P<part_no>\S+)\s*\n"
        r"^\s*(HW_revision|[Rr]evision|Hardware\s+revision):\s+(?P<revision>\S+)\s*\n"
        r"^\s*(SN|Serial\s+number):\s+(?P<serial>\S+)",
        re.MULTILINE,
    )
    rx_pwr = re.compile(r"^\s+Module\s+(?P<num>\d+):\s+(?P<part_no>PM\S+)", re.MULTILINE)

    rx_version = re.compile(
        r"^Eltex (?P<platform>\S+) software version (?P<version>\S+\s+build\s+\d+)\s*"
    )

    def get_count_ports(self):
        return 16, 8 if self.is_LTP16N else 8, 4  # PON-ports, Front-ports

    def execute_snmp(self, **kwargs):
        count_ports = self.get_count_ports()
        v = self.scripts.get_version()
        r = [{"type": "CHASSIS", "vendor": "ELTEX", "part_no": v["platform"]}]
        serial = self.capabilities.get("Chassis | Serial Number")
        if serial:
            r[-1]["serial"] = serial
        revision = self.capabilities.get("Chassis | HW Version")
        if revision:
            r[-1]["revision"] = revision

        # Power Supply (2 x slots)
        for id in [1, 2]:
            pwr_pn = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.4.1.3.{id}")
            pwr_pn = pwr_pn.split()[0]
            r += [{"type": "PSU", "vendor": "ELTEX", "part_no": pwr_pn, "number": id - 1}]

        # SFP for 8 x Fron-port (Uplinks)
        for id in range(1, count_ports[1] + 1):
            vendor = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.2.{id}")
            part_no = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.3.{id}")
            revision = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.6.6.1.4.{id}")
            if part_no != "":
                r += [
                    {
                        "type": "XCVR",
                        "number": id,
                        "vendor": re.sub(r"\s+$", "", vendor),
                        "part_no": re.sub(r"\s+$", "", part_no),
                        "revision": re.sub(r"\s+$", "", revision),
                    }
                ]

        # SFP for 16 x PON-port
        for id in range(1, count_ports[0] + 1):
            vendor = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.5.1.{id}")
            part_no = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.6.1.{id}")
            revision = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.4.3.1.1.7.1.{id}")
            if part_no != "":
                r += [
                    {
                        "type": "XCVR",
                        "number": str(id + count_ports[1]),
                        "vendor": re.sub(r"\s+$", "", vendor),
                        "part_no": re.sub(r"\s+$", "", part_no),
                        "revision": re.sub(r"\s+$", "", revision),
                    }
                ]

        for res in r:
            if res["type"] == "CHASSIS":
                res.update({"sensors": self.get_chassis_sensors()})
        return r

    def get_chassis_sensors(self):
        r = []
        # Fan State
        for id in range(4):
            state = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.2.{id+6}.0")
            if state != 1:
                state = 0
            r += [
                {
                    "name": f"Fan-{id+1}",
                    "status": bool(state),
                    "description": f"State of Fan-{id+1}",
                    "measurement": "StatusEnum",
                    "labels": [
                        "noc::sensor::placement::internal",
                        "noc::sensor::mode::flag",
                        "noc::sensor::target::fan",
                    ],
                    "snmp_oid": f"1.3.6.1.4.1.35265.1.209.1.2.{id+6}.0",
                }
            ]

        # Power Supply State
        for oid, v in self.snmp.getnext("1.3.6.1.4.1.35265.1.209.1.4.1.2"):
            sindex = oid[len("1.3.6.1.4.1.35265.1.209.1.4.1.2") + 1 :]
            # If Power Supply module present
            if v == 1:
                state = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.4.1.5.{sindex}")
                if state != 1:
                    state = 0

                r += [
                    {
                        "name": f"PS-{sindex}",
                        "status": bool(state),
                        "description": f"State of Power Supply {sindex}",
                        "measurement": "StatusEnum",
                        "labels": [
                            "noc::sensor::placement::internal",
                            "noc::sensor::mode::flag",
                            "noc::sensor::target::supply",
                        ],
                        "snmp_oid": f"1.3.6.1.4.1.35265.1.209.1.4.1.5.{sindex}",
                    }
                ]

        # Temperature Sensor
        temp_sensor_map = {"16": "PON SFP 1", "17": "PON SFP 2", "18": "Front SFP", "19": "Switch"}

        for id in range(16, 20):
            v = self.snmp.get(f"1.3.6.1.4.1.35265.1.209.1.2.{id}.0")
            if v:
                state = 1
            else:
                state = 0

            r += [
                {
                    "name": f"Temperature Sensor {temp_sensor_map[str(id)]}",
                    "status": bool(state),
                    "description": f"Temperature sensor for {temp_sensor_map[str(id)]}",
                    "measurement": "Celsius",
                    "labels": [
                        "noc::sensor::placement::internal",
                        "noc::sensor::mode::temperature",
                    ],
                    "snmp_oid": f"1.3.6.1.4.1.35265.1.209.1.2.{id}.0",
                }
            ]

        return r

    def execute_cli(self, **kwargs):
        count_ports = self.get_count_ports()
        try:
            v = self.cli("show system environment", cached=True)
        except self.CLISyntaxError:
            raise NotImplementedError
        match = self.rx_platform.search(v)
        platform = match.group("part_no")
        serial = match.group("serial")
        rev = match.group("revision")
        ver = self.cli("show version", cached=True)
        match = self.rx_version.search(ver)
        # if platform:
        #    platform = match.group("platform")
        r = [
            {
                "type": "CHASSIS",
                "vendor": "ELTEX",
                "part_no": platform,
                "serial": serial,
                "revision": rev,
            }
        ]

        for match in self.rx_pwr.finditer(v):
            r += [
                {
                    "type": "PSU",
                    "vendor": "ELTEX",
                    "part_no": match.group("part_no"),
                    "number": match.group("num"),
                }
            ]

        # SFP for 8 x Fron-port (Uplinks)
        try:
            v = self.cli(f"show interface front-port 1-{count_ports[1]} sfp", cached=True)
            for i in parse_table(v, line_wrapper=None):
                if i[2] != "-":
                    r += [
                        {
                            "type": "XCVR",
                            "number": i[0],
                            "vendor": i[1],
                            "part_no": i[2],
                        }
                    ]
        except self.CLISyntaxError:
            raise NotImplementedError

        # SFP for 16 x PON-port
        try:
            v = self.cli(f"show interface pon-port 1-{count_ports[0]} state", cached=True)
            for i in parse_table(v, line_wrapper=None):
                if i[5] != "-":
                    r += [
                        {
                            "type": "XCVR",
                            "number": str(int(i[0]) + count_ports[1]),
                            "vendor": i[4],
                            "part_no": i[5],
                        }
                    ]
        except self.CLISyntaxError:
            raise NotImplementedError

        for res in r:
            if res["type"] == "CHASSIS" and self.has_snmp():
                res.update({"sensors": self.get_chassis_sensors()})
        return r
