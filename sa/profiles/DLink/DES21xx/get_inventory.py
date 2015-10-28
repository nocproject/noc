# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_inventory
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
import re


class Script(BaseScript):
    name = "DLink.DES21xx.get_inventory"
    cache = True
    interface = IGetInventory
    rx_ver = re.compile(r"Product Name:(?P<platform>\S+).+Firmware Version:(?P<version>\S+)", re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch"))
        return [{
            "type": "CHASSIS",
            "number": "1",
            "vendor": "DLINK",
            "part_no": [match.group("platform")]
        }]
