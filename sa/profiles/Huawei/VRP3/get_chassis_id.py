# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Huawei.VRP3.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "Huawei.VRP3.get_chassis_id"
    implements = [IGetChassisID]
    rx_mac = re.compile(r"^\s*MAC address:\s+(?P<mac>\S+)")

    def execute(self):
        match = self.re_search(self.rx_mac,
            self.cli("show atmlan mac-address"))
        return match.group("mac")
