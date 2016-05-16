# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Cisco.SANOS.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
from itertools import groupby
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Cisco.SANOS.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\",\s+DESCR: \"(?P<descr>[^\"]+)\"\s*\n"
        r"PID:\s+(?P<pid>\S+)?\s*,\s+VID:\s+(?P<vid>[\S ]+)?\n,\s+"
        r"SN: (?P<serial>\S+)?", re.MULTILINE | re.DOTALL)

    def get_type(self, name, pid=None, descr=None):
        """
        Get type, number and part_no
        """
        if pid is None:
            pid = ""
        if name.startswith("Chassic"):
            return "CHASSIC", None, pid
        if name.startswith("Slot "):
            if "Supervisor" in descr:
                return "SUP", name[6:], pid
            elif "Services Module" in descr:
                return "SERV", name[6:], pid
            elif "Power Supply" in descr:
                return "PSU", name[6:], pid
            elif "Fan Module" in descr:
                return "FAN", name[6:], pid
            else:
                return None, None, None

    def execute(self):
        objects = []
        try:
            v = self.cli("show inventory")
            for match in self.rx_item.finditer(v):
                vendor, serial = "", ""
                n =  match.group("name")
                p =  match.group("pid")
                d =  match.group("descr")
                type, number, part_no = self.get_type(
                    match.group("name"), match.group("pid"),
                    match.group("descr")
                )
                serial = match.group("serial")
                vendor = "CISCO"
                objects += [{
                    "type": type,
                    "number": number,
                    "vendor": vendor,
                    "serial": serial,
                    "description": match.group("descr"),
                    "part_no": [part_no],
                    "revision": match.group("vid"),
                    "builtin": False
                }]
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        print "%s" % objects
        return objects

