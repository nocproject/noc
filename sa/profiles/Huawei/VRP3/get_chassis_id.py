# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(BaseScript):
    name = "Huawei.VRP3.get_chassis_id"
    interface = IGetChassisID
    rx_mac = re.compile(r"^\s*MAC address:\s+(?P<mac>\S+)")

    def execute(self):
        match = self.re_search(self.rx_mac,
            self.cli("show atmlan mac-address"))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
