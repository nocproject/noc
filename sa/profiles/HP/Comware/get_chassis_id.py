# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.Comware.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "HP.Comware.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(r"^\s*MAC_ADDRESS\s+:\s+(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_id, self.cli("display device manuinfo",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }

