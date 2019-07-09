# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# InfiNet.WANFlexX.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "InfiNet.WANFlexX.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"PortID:       \|\s*(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_mac, self.cli("lldp local\n"))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
