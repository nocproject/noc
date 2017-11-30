# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Cisco.SMB.get_inventory
# ----------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
from itertools import groupby
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetinventory import IGetInventory
from noc.sa.interfaces.base import InterfaceTypeError


class Script(BaseScript):
    name = "Cisco.SMB.get_inventory"
    interface = IGetInventory

    rx_item = re.compile(
        r"^NAME: \"(?P<name>[^\"]+)\"\s* DESCR: \"(?P<descr>[^\"]+)\"\s*\n"
        r"PID:\s+(?P<pid>\S+)?\s* VID:\s*(?P<vid>[\S ]+)?\s* SN: (?P<serial>\S+)\s*"
        , re.MULTILINE | re.DOTALL)

    def execute(self):
        match = self.rx_item.search(self.cli("show inventory"))
        return [{
            "type": "CHASSIS",
            "vendor": "CISCO",
            "part_no": [match.group("pid")],
            "revision": match.group("vid"),
            "serial": match.group("serial"),
            "description": match.group("descr")
        }]
