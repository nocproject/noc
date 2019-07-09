# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXDSL98xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "ZTE.ZXDSL98xx.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"MAC address\s+: ((?:[0-9A-F]{2}[:\-]){5}[0-9A-F]{2})")

    def execute_cli(self):
        macs = sorted(self.rx_mac.findall(self.cli("show mac")))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
