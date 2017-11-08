# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# HP.Comware.get_inventory
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory


class Script(BaseScript):
    name = "HP.Comware.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^(?P<type>Unit|Slot| Subslot) (?P<slot>\d+):?\n"
        r"^\s*DEVICE_NAME\s*: (?P<name>.+?)\n"
        r"^\s*DEVICE_SERIAL_NUMBER\s*: (?P<serial>\S+)\n"
        r"(^\s*MAC_ADDRESS\s+: \S+\n)?"
        r"^\s*MANUFACTURING_DATE\s*: (?P<mdate>\S+)\n"
        r"^\s*VENDOR_NAME\s*: (?P<vendor>\S+)\n", re.MULTILINE)
    rx_name = re.compile(r"^(?P<name>.+) (?P<part_no>\S+)?")

    def execute(self):
        objects = []
        try:
            v = self.cli("display device manuinfo", cached=True)
            for match in self.rx_item.finditer(v):
                vendor = match.group("vendor")
                serial = match.group("serial")
                if match.group("type") in ["Slot", "Unit"]:
                    type = "CHASSIS"
                if match.group("type").strip() == "Subslot":
                    type = "MODULE"
                n = match.group("name")
                if n.find(" ") != -1:
                    descr = self.rx_name.search(n).group("name")
                    part_no = self.rx_name.search(n).group("part_no")
                else:
                    descr = ""
                    part_no = n
                objects += [{
                    "type": type,
                    "number": match.group("slot"),
                    "builtin": False,
                    "vendor": vendor,
                    "part_no": [part_no],
                    "serial": serial,
                    "mfg_date": match.group("mdate"),
                    "description": descr
                }]
        except self.CLISyntaxError:
            raise self.NotSupportedError()
        return objects
