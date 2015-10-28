# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DGS3100.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DGS3100.get_chassis_id"
    cache = True
    interface = IGetChassisID
    rx_mac = re.compile(r"^MAC Address\s+\:\s+(?P<mac>\S+)\s*$",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        v = self.cli("show switch", cached=True)
        match = self.re_search(self.rx_mac, v)
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
