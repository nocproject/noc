# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOSXR.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(NOCScript):
    name = "Cisco.IOSXR.get_inventory"
    implements = [IGetInventory]

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S+)\s*,\s+VID:\s+(?P<vid>\S*)\s*, SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )
    rx_trans = re.compile("(1000Base\S+)")

    TRANS_MAP = {
        "1000BASELX": "NoName | Transceiver | 1G | SFP LX",
        "1000BASELH": "NoName | Transceiver | 1G | SFP LH",
        "1000BASEZX": "NoName | Transceiver | 1G | SFP ZX",
        "1000BASEBX10D": "NoName | Transceiver | 1G | SFP BX (tx 1490nm)",
        "1000BASEBX10U": "NoName | Transceiver | 1G | SFP BX (tx 1310nm)",
        "1000BASET": "NoName | Transceiver | 1G | SFP TX"
    }

    def execute(self):
        objects = []
        v = self.cli("admin show inventory")
        for match in self.rx_item.finditer(v):
            type, number, part_no = self.get_type(
                match.group("name"), match.group("pid"),
                match.group("descr"), len(objects)
            )
            if not part_no:
                print "!!! UNKNOWN: ", match.groupdict()
                continue
            else:
                vendor = "CISCO" if "NoName" not in part_no else "NONAME"
                objects += [{
                    "type": type,
                    "number": number,
                    "vendor": vendor,
                    "serial": match.group("serial"),
                    "description": match.group("descr"),
                    "part_no": [part_no],
                    "revision": match.group("vid"),
                    "builtin": False
                }]
        # Reorder chassis
        if objects[-1]["type"] == "CHASSIS":
            objects = [objects[-1]] + objects[:-1]
        return objects

    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if "RSP" in pid:
            number = name.split()[1].split("/")[1][3]
            return "RSP", number, pid
        elif "MOD" in pid:
            number = name.split()[1].split("/")[1]
            return "MOD", number, pid
        elif "MPA" in pid:
            number = name.split()[1].split("/")[-1]
            return "MPA", number, pid
        elif "XFP" in pid or "GLC" in pid or "SFP" in pid:
            number = name.split()[2].split("/")[-1]
            return "XCVR", number, pid
        elif "FAN" in pid:
            number = name.split()[1].split("/")[1][2]
            return "FAN", number, pid
        elif "Power Module" in descr:
            # number = 0/PM0/SP
            number = name.split()[1].split("/")[1][2:]
            return "PWR", number, pid
        elif name.startswith("chassis"):
            return "CHASSIS", None, pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr)
        if match:
            return self.TRANS_MAP.get(match.group(1).upper())
        return None