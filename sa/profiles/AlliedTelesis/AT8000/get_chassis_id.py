# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^\s*MAC Address\s*\.+ (?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self):
        v = self.cli("show switch", cached=True)
        match = self.rx_mac.search(v)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
