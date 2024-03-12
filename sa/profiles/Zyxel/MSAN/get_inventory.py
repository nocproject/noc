# ---------------------------------------------------------------------
# Zyxel.MSAN.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.core.text import parse_table


class Script(BaseScript):
    name = "Zyxel.MSAN.get_inventory"
    interface = IGetInventory
    cache = True

    rx_slot = re.compile(
        r"^\s*slot(?P<number>\d+):\s*\n"
        r"^\s*name\s*:\s+(?P<part_no>\S+)\s*\n"
        r"^.+?\n"
        r"^\s*hardware version\s*:\s+(?P<revision>\S+)\s*\n"
        r"^\s*hardware serial number\s*:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL,
    )

    rx_hw = re.compile(
        r"^\s*Model\s*:\s+(?:\S+ \/ )?(?P<part_no>\S+)\s*\n"
        r"^.+?\n"
        r"^\s*Hardware version\s*:\s+(?P<revision>\S+)\s*\n"
        r"^\s*Serial number\s*:\s+(?P<serial>\S+)\s*\n",
        re.MULTILINE | re.DOTALL,
    )
    rx_hw2 = re.compile(
        r"^\s*Hardware Version: (?P<revision>\S+|not defined)\s*\n"
        r"^\s*Serial Number: (?P<serial>\S+|not defined)\s*\n",
        re.MULTILINE,
    )
    rx_chips = re.compile(r"^\s*(?P<platform>\S+?)([/ ](?P<module>\S+))?\s+")

    M_TYPE = {
        "IES-2000": "MSC1000",
        "IES-2000M": "MSC1000A",
        "IES-3000": "MSC1000",
        "IES-3000M": "MSC1000A",
    }

    def get_sensors(self, slot_index):
        r = []

        if slot_index == 1:  # Fan sensors on chassis only
            # Fan state
            for oid, name in self.snmp.getnext("1.3.6.1.4.1.890.1.5.13.1.2.1.1.6.0"):
                sindex = oid.split(".")[-1]
                cur_value = self.snmp.get(f"1.3.6.1.4.1.890.1.5.13.1.2.1.1.2.0.{sindex}")
                try:
                    cur_value = int(cur_value)
                    status = bool(cur_value)
                except:
                    status = False

                r += [
                    {
                        "name": f"{slot_index}|{name}",
                        "status": status,
                        "description": f"Скорость вращения {name} устройства",
                        "measurement": "rpm",
                        "labels": [
                            "noc::sensor::placement::internal",
                            "noc::sensor::mode::flag",
                            "noc::sensor::target::fan",
                        ],
                        "snmp_oid": f"1.3.6.1.4.1.890.1.5.13.1.2.1.1.2.0.{sindex}",
                    }
                ]

        # Voltage state
        for oid, name in self.snmp.getnext(f"1.3.6.1.4.1.890.1.5.13.1.2.2.1.7.0.{slot_index}"):
            sindex = oid.split(".")[-1]
            cur_value = self.snmp.get(f"1.3.6.1.4.1.890.1.5.13.1.2.2.1.2.0.{slot_index}.{sindex}")
            try:
                cur_value = int(cur_value)
                status = bool(cur_value)
            except:
                status = False
            r += [
                {
                    "name": f"{slot_index}|{name}",
                    "status": status,
                    "description": "Напряжение питания устройства",
                    "measurement": "Volt AC",
                    "labels": [
                        "noc::sensor::placement::internal",
                        "noc::sensor::mode::voltage",
                        "noc::sensor::target::supply",
                    ],
                    "snmp_oid": f"1.3.6.1.4.1.890.1.5.13.1.2.2.1.2.0.{slot_index}.{sindex}",
                }
            ]
        # Temperature state
        for oid, name in self.snmp.getnext(f"1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.6.0.{slot_index}"):
            sindex = oid.split(".")[-1]
            cur_value = self.snmp.get(
                f"1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.2.0.{slot_index}.{sindex}"
            )
            try:
                cur_value = int(cur_value)
                status = bool(cur_value)
            except:
                status = False
            r += [
                {
                    "name": f"{slot_index}|{name}",
                    "status": status,
                    "description": "Значение температуры с внутреннего датчика",
                    "measurement": "Celsius",
                    "labels": [
                        "noc::sensor::placement::internal",
                        "noc::sensor::mode::temperature",
                    ],
                    "snmp_oid": f"1.3.6.1.4.1.890.1.5.13.5.11.3.3.1.2.0.{slot_index}.{sindex}",
                }
            ]

        return r

    def execute(self):
        r = []
        slots = self.profile.get_slots_n(self)
        version = self.scripts.get_version()
        if slots > 1:
            if version["platform"] not in ["IES-2000", "IES-2000M", "IES-3000", "IES-3000M"]:
                for i in range(1, slots + 1):
                    match = self.rx_slot.search(self.cli("lcman show %s" % i))
                    if match:
                        part_no = match.group("part_no")
                        r += [
                            {
                                "type": "LINECARD",
                                "number": match.group("number"),
                                "vendor": "ZYXEL",
                                "part_no": match.group("part_no"),
                                "serial": match.group("serial"),
                                "revision": match.group("revision"),
                            }
                        ]
                        c = self.profile.get_platform(self, slots, part_no)
                        if c:
                            r.insert(0, {"type": "CHASSIS", "vendor": "ZYXEL", "part_no": c})
            else:
                r += [{"type": "CHASSIS", "vendor": "ZYXEL", "part_no": version["platform"]}]
                t = parse_table(self.cli("lcman show", cached=True))
                for i in t:
                    if i[1] == "-":
                        continue
                    part_no = i[2]
                    if part_no == "msc":
                        part_no = self.M_TYPE[version["platform"]]
                    r += [
                        {"type": "LINECARD", "number": i[0], "vendor": "ZYXEL", "part_no": part_no}
                    ]
            for i in r:
                if i["type"] == "CHASSIS" and self.has_snmp():
                    i.update({"sensors": self.get_sensors(1)})
                if i["type"] == "LINECARD" and self.has_snmp():
                    i.update({"sensors": self.get_sensors(i["number"])})
        else:
            module = None
            match = self.rx_hw.search(self.cli("sys info show", cached=True))
            if match:
                c = self.profile.get_platform(self, slots, match.group("part_no"))
                if match.group("part_no").startswith("AAM"):
                    module = match.group("part_no")
            else:
                match1 = self.rx_chips.search(self.cli("chips info", cached=True))
                c = match1.group("platform")
                module = match1.group("module")
                match = self.rx_hw2.search(self.cli("sys info show", cached=True))
            r = [
                {
                    "type": "CHASSIS",
                    "vendor": "ZYXEL",
                    "part_no": c,
                }
            ]
            if match.group("serial") != "not defined" and match.group("revision") != "not defined":
                r[0]["serial"] = match.group("serial")
                r[0]["revision"] = match.group("revision")
            if module:
                r += [{"type": "LINECARD", "number": 1, "vendor": "ZYXEL", "part_no": module}]
            for i in r:
                if i["type"] == "CHASSIS" and self.has_snmp():
                    i.update({"sensors": self.get_sensors(1)})
                if i["type"] == "LINECARD" and self.has_snmp():
                    i.update({"sensors": self.get_sensors(i["number"])})
        return r
