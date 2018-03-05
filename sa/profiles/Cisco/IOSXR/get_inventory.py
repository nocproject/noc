# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Cisco.IOSXR.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2013 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Cisco.IOSXR.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\",? DESCR: \"(?P<descr>[^\"]+)\"\n"
        r"PID:\s+(?P<pid>\S*)\s*,?\s+VID:\s+(?P<vid>\S*)\s*,? SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE
    )

    rx_trans = re.compile("((?:100|1000|10G)BASE\S+)")

    def execute(self):
        objects = []
        v = self.cli("admin show inventory")
        for match in self.rx_item.finditer(v):
            type, number, part_no = self.get_type(
                match.group("name"), match.group("pid"),
                match.group("descr"), len(objects)
            )
            if not part_no:
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
        if "RSP" in pid or "RSP" in name:
            number = name.split()[1].split("/")[1][3]
            return "RSP", number, pid
        elif "A9K-MODULEv" in pid:
            number = name.split()[1].split("/")[-1]
            return "MPA", number, pid
        elif "MOD" in pid:
            number = name.split()[1].split("/")[1]
            return "MOD", number, pid
        elif (
            (
                "LC" in descr or "Line Card" in descr or "Linecard" in descr
            ) and "module mau" not in name and not name.startswith("chassis")
        ):
            number = name.split()[1].split("/")[1]
            return "MOD", number, pid
        elif "MPA" in pid:
            number = name.split()[1].split("/")[-1]
            return "MPA", number, pid
        elif "XFP" in pid or "GLC" in pid or "SFP" in descr:
            number = name.split()[2].split("/")[-1]
            if not pid:
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return None, None, None
            return "XCVR", number, pid
        elif "FAN" in pid:
            number = name.split()[1].split("/")[1][2]
            return "FAN", number, pid
        elif ("Power Module" in descr or
              "Power Supply" in descr):
            # number = 0/PM0/SP
            number = name.split()[1].split("/")[1][2:]
            return "PWR", number, pid
        elif name.startswith("chassis"):
            return "CHASSIS", None, pid
        elif name.startswith("Rack") and "Slot Single Chassis" in descr:
            return "CHASSIS", None, pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr)
        if match:
            return "Unknown | Transceiver | %s" % match.group(1).upper()
        return "Unknown | Transceiver | Unknown"
