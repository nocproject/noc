# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Iskratel.ESCOM.get_chassis_id
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
    name = "Iskratel.ESCOM.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_mac_oob = re.compile(
        r"^System MAC Address:\s+(?P<mac>\S+)\s*\n"
        r"^OOB MAC Address:\s+(?P<oob>\S+)", re.MULTILINE)

    def execute(self):
        match = self.rx_mac.search(self.cli("show system", cached=True))
        if match:
            return {
                "first_chassis_mac": match.group("mac"),
                "last_chassis_mac": match.group("mac")
            }
        match = self.rx_mac_oob.search(
            self.cli("show system unit 1", cached=True)
        )
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("oob")
        }
