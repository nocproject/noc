# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_inventory
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
    name = "HP.Comware.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^(?P<type>Slot| Subslot) (?P<slot>\d+):\n"
        r"^DEVICE_NAME\s+: (?P<name>.+?)\n"
        r"^DEVICE_SERIAL_NUMBER\s+: (?P<serial>\S+)\n"
        r"(^MAC_ADDRESS\s+: \S+\n)?"
        r"^MANUFACTURING_DATE\s+: (?P<mdate>\S+)\n"
        r"^VENDOR_NAME\s+: (?P<vendor>\S+)\n", re.MULTILINE)
    rx_name = re.compile(r"^(?P<name>.+) (?P<part_no>\S+)?")

    def execute(self):
        objects = []
        try:
            v = self.cli("display device manuinfo", cached=True)
            for match in self.rx_item.finditer(v):
                vendor = match.group("vendor")
                serial = match.group("serial")
                if match.group("type") == "Slot":
                    type = "CHASSIS"
                if match.group("type").strip() == "Subslot":
                    type = "MODULE"
                n = match.group("name")
                descr = self.rx_name.search(n).group("name")
                part_no = self.rx_name.search(n).group("part_no")
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

