# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# UPVEL.UP.get_chassis_id
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
    name = "UPVEL.UP.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^Bridge ID\s+: \d+\.(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        v = self.cli("show spanning-tree", cached=True)
        match = self.rx_mac.search(v)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
