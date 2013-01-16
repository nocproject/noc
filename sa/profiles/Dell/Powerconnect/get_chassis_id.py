# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Dell.Powerconnect.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "Dell.Powerconnect.get_chassis_id"
    cache = True
    rx_mac = re.compile(r"Burned In MAC Address\.+ (?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    implements = [IGetChassisID]

    def execute(self):
        match = self.re_search(self.rx_mac, self.cli("show tech-support",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
