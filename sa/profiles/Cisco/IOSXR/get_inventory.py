# ---------------------------------------------------------------------
# Cisco.IOSXR.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2023 The NOC Project
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
        r"PID:\s+(?P<pid>\S*?)\s*,?\s+VID:\s+(?P<vid>\S*?)\s*,? SN: (?P<serial>\S+)",
        re.MULTILINE | re.DOTALL | re.IGNORECASE,
    )
    # Found in ASR9K ver 7.1.3
    rx_item2 = re.compile(
        r"^\s+Name: (?P<name>.+?)\s+Descr: (?P<descr>.+?)\s*\n"
        r"^\s+PID: (?P<pid>\S+)\s+VID: (?P<vid>\S+)\s+SN: (?P<serial>\S+)\s*\n",
        re.MULTILINE,
    )
    rx_new_type = re.compile(r"^\d/(?:RSP|FT|PT|PT0-PM|)(?P<number>\d+)$")
    rx_new_chass = re.compile(r"^ASR \d+ Chassis$")

    rx_trans = re.compile(r"((?:100|1000|10G)BASE\S+)")

    def execute(self):
        objects = []
        v = self.cli("admin show inventory")
        if self.rx_item.search(v):
            rx_search = self.rx_item
        else:
            rx_search = self.rx_item2
        for match in rx_search.finditer(v):
            self.logger.debug(
                "Get type: %s, %s, %s",
                match.group("name"),
                match.group("pid"),
                match.group("descr"),
            )
            type, number, part_no = self.get_type(
                match.group("name"), match.group("pid"), match.group("descr"), len(objects)
            )
            self.logger.debug("Return: %s, %s, %s", type, number, part_no)
            if not part_no:
                continue
            vendor = "CISCO" if "NoName" not in part_no else "NONAME"
            objects += [
                {
                    "type": type,
                    "number": number,
                    "vendor": vendor,
                    "serial": match.group("serial"),
                    "description": match.group("descr"),
                    "part_no": [part_no],
                    "revision": match.group("vid"),
                    "builtin": False,
                }
            ]
        # Reorder chassis
        if objects[-1]["type"] == "CHASSIS":
            objects = [objects[-1], *objects[:-1]]
        return objects

    def get_type(self, name, pid, descr, lo):
        """
        Get type, number and part_no
        """
        if "RSP" in pid or "RSP" in name:
            match = self.rx_new_type.search(name)
            if match:
                return "RSP", match.group("number"), pid
            number = name.split()[1].split("/")[1][3]
            return "RSP", number, pid
        if "A9K-MODULEv" in pid:
            number = name.split()[1].split("/")[-1]
            return "MPA", number, pid
        if "MOD" in pid:
            number = name.split()[1].split("/")[1]
            return "MOD", number, pid
        if (
            (
                "LC" in descr
                or "Line Card" in descr
                or "Line card" in descr
                or "Linecard" in descr
                or "Interface Module" in descr
            )
            and "module mau" not in name
            and not name.startswith("chassis")
        ):
            match = self.rx_new_type.search(name)
            if match:
                return "MOD", match.group("number"), pid
            number = name.split()[1].split("/")[1]
            return "MOD", number, pid
        if "MPA" in pid:
            number = name.split()[1].split("/")[-1]
            return "MPA", number, pid
        if "XFP" in pid or "GLC" in pid or "CFP-" in pid or "SFP" in descr:
            try:
                name = name.split()[2]
            except IndexError:
                pass
            number = name.split("/")[-1]
            if not pid:
                pid = self.get_transceiver_pid(descr)
                if not pid:
                    return None, None, None
            return "XCVR", number, pid
        if "FAN" in pid:
            match = self.rx_new_type.search(name)
            if match:
                return "FAN", match.group("number"), pid
            number = name.split()[1].split("/")[1][2]
            return "FAN", number, pid
        if "Power Module" in descr or "Power Supply" in descr or "AC Power" in descr:
            match = self.rx_new_type.search(name)
            if match:
                return "PWR", match.group("number"), pid
            numbers = name.split()[1].split("/")
            if len(numbers) == 4:  # 0/PS0/M1/SP
                number = numbers[2][1:]
            else:  # 0/PM0/SP
                number = numbers[1][2:]
            return "PWR", number, pid
        if "Power Tray" in descr:
            match = self.rx_new_type.search(name)
            return "PT", match.group("number"), pid
        if name.startswith("chassis"):
            return "CHASSIS", None, pid
        if name.startswith("Rack") and (
            "Slot Single Chassis" in descr or self.rx_new_chass.search(descr)
        ):
            return "CHASSIS", None, pid
        # Unknown
        return None, None, None

    def get_transceiver_pid(self, descr):
        match = self.rx_trans.search(descr)
        if match:
            return "Unknown | Transceiver | %s" % match.group(1).upper()
        return "Unknown | Transceiver | Unknown"
