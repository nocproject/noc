# ---------------------------------------------------------------------
# Cisco.SANOS.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "Cisco.SANOS.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\",\s+DESCR: \"(?P<descr>[^\"]+)\"\s*\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>[\S ]+)?\n,\s+"
        r"SN: (?P<serial>\S+)?",
        re.MULTILINE | re.DOTALL,
    )

    def get_type(self, name, pid, descr):
        """
        Get type, number and part_no
        """
        if pid is None:
            pid = ""
        if name.startswith("Chassis"):
            return "CHASSIC", None, pid
        if name.startswith("Slot "):
            if "Supervisor" in descr:
                return "SUP", name[5:], pid
            if "Services Module" in descr:
                return "SERV", name[5:], pid
            if "Power Supply" in descr:
                return "PSU", name[5:], pid
            if "Fan Module" in descr:
                if pid == "" and descr.startswith("MDS 9"):
                    s = descr.split()
                    pid = ("%s-%s-%s" % (s[0], s[1], s[2])).upper()
                return "FAN", name[5:], pid
            return None, None, None
        return None, None, None

    def execute(self):
        objects = []
        try:
            v = self.cli("show inventory")
            for match in self.rx_item.finditer(v):
                vendor, serial = "", ""
                type, number, part_no = self.get_type(
                    match.group("name"), match.group("pid"), match.group("descr")
                )
                serial = match.group("serial")
                vendor = "CISCO"
                objects += [
                    {
                        "type": type,
                        "number": number,
                        "vendor": vendor,
                        "serial": serial,
                        "description": match.group("descr"),
                        "part_no": [part_no],
                        "revision": match.group("vid"),
                        "builtin": False,
                    }
                ]
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return objects
