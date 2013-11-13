# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.IOS.get_inventory
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
    name = "Cisco.IOS.get_inventory"
    implements = [IGetInventory]

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\", DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID: (?P<pid>\S+)\s*, VID:\s+(?P<vid>\S*)\s*, SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL
    )
    rx_trans = re.compile("(1000Base..)")

    TRANS_MAP = {
        "1000BASELX": "NoName | Transceiver | 1G | SFP LX",
        "1000BASELH": "NoName | Transceiver | 1G | SFP LH",
        "1000BASEZX": "NoName | Transceiver | 1G | SFP ZX"
    }

    def execute(self):
        objects = []
        v = self.cli("show inventory")
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
        return objects

    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if descr.startswith("Transceiver") or name.startswith("GigabitEthernet"):
            # Transceivers
            # Get number
            if name.startswith("Transceiver "):
                # Get port number
                _, number = name.rsplit("/", 1)
            elif name.startswith("GigabitEthernet"):
                number = name.split(" ", 1)[0].split("/")[-1]
            else:
                number = None
            if pid in ("N/A", "Unspecified"):
                # Non-Cisco transceivers
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return None, None, None
                else:
                    return "XCVR", number, pid
            else:
                return "XCVR", number, pid
        elif lo == 0 or pid.startswith("CISCO") or pid.startswith("WS-C"):
            return "CHASSIS", None, pid
        elif name.startswith("module "):
            # Linecards or supervisors
            if pid.startswith("RSP"):
                return "SUP", name[7:], pid
            else:
                return "LINECARD", name[7:], pid
        elif "-DFC" in pid:
            # DFC subcard
            return "DFC", None, pid
        elif name.startswith("PS "):
            # Power supply
            return "PSU", name.split()[1], pid
        elif name.startswith("Power Supply "):
            return "PSU", name.split()[2], pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr)
        if match:
            return self.TRANS_MAP.get(match.group(1).upper())
        return None