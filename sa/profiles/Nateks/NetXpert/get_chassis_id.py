# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Nateks.NetXpert.get_chassis_id
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
    name = "Nateks.NetXpert.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"MAC Address:\s*(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_mac, self.cli("sh ver\n"))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
