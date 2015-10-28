# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect55xx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(BaseScript):
    name = "Dell.Powerconnect55xx.get_chassis_id"
    cache = True
    rx_mac = re.compile(r"System MAC Address:\s+(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    interface = IGetChassisID

    def execute(self):
        match = self.re_search(self.rx_mac, self.cli("show system unit 1",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
