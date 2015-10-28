# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DxS.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^MAC Address\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    interface = IGetChassisID

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
