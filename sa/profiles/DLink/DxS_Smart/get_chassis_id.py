# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS_Smart.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2014 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "DLink.DxS_Smart.get_chassis_id"
    cache = True
    implements = [IGetChassisID]

    rx_ver = re.compile(r"^MAC Address\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_ver,
            self.cli("show switch", cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
