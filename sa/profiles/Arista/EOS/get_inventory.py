# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Arista.EOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.lib.text import parse_table


class Script(NOCScript):
    name = "Arista.EOS.get_inventory"
    cache = True
    implements = [IGetInventory]

    rx_section = re.compile("System has (\d+) (.+?)$", re.MULTILINE)

    def execute(self):
        objects = []
        v = self.cli("show inventory")
        sections = self.rx_section.split(v)
        objects += self.parse_chassis(sections.pop(0))
        while sections:
            cnt, type, data = sections[:3]
            sections = sections[3:]
            t = type.lower()
            if t.startswith("power supply"):
                objects += self.parse_psu(data)
            elif t.startswith("fan"):
                objects += self.parse_fan(data)
            elif t.startswith("transceiver"):
                objects += self.parse_transceiver(data)
        return objects

    @classmethod
    def parse_chassis(cls, data):
        objects = []
        parts = data.split("\n\n")
        # Chassis section
        _, ctable = parts[0].split("\n", 1)
        n = 0
        for part_no, description in parse_table(ctable):
            objects += [{
                "type": "CHASSIS",
                "number": str(n),
                "vendor": "ARISTA",
                "serial": None,
                "description": description,
                "part_no": part_no,
                "revision": None,
                "builtin": False
            }]
            n += 1
        # Serial/revision section
        n = 0
        for rev, serial, mfg_data in parse_table(parts[1]):
            objects[n]["revision"] = rev
            objects[n]["serial"] = serial
            n += 1
        return objects

    @classmethod
    def parse_psu(cls, data):
        objects = []
        for slot, part_no, serial in parse_table(data.strip()):
            objects += [{
                "type": "PWR",
                "number": slot,
                "vendor": "ARISTA",
                "serial": serial,
                "part_no": part_no,
                "builtin": False
            }]
        return objects

    @classmethod
    def parse_fan(cls, data):
        objects = []
        for slot, nfans, part_no, serial in parse_table(data.strip()):
            objects += [{
                "type": "FAN",
                "number": slot,
                "vendor": "ARISTA",
                "serial": serial,
                "part_no": part_no,
                "builtin": False
            }]
        return objects

    @classmethod
    def parse_transceiver(cls, data):
        objects = []
        for port, vendor, part_no, serial, rev in parse_table(data.strip()):
            vendor = vendor.upper()
            if vendor == "NOT PRESENT":
                continue
            if vendor == "ARISTA NETWORKS":
                vendor = "ARISTA"
            objects += [{
                "type": "XCVR",
                "number": port,
                "vendor": vendor,
                "serial": serial,
                "part_no": part_no,
                "builtin": False
            }]
        return objects
