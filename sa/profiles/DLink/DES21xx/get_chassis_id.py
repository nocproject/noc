# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DES21xx.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetChassisID
import re


class Script(NOCScript):
    name = "DLink.DES21xx.get_chassis_id"
    cache = True
    rx_ver = re.compile(r"^MAC address:(?P<id>\S+)", re.IGNORECASE | re.MULTILINE)
    implements = [IGetChassisID]

    def execute(self):
        match = self.re_search(self.rx_ver, self.cli("show switch"))
        return match.group("id")
