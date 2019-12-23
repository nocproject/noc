# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Raisecom.ROS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Raisecom.ROS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac_search = re.compile(
        r"(System MacAddress is|System MacAddress|System MAC Address|System MacAddress( is)?)\s*:\s*(?P<mac>\S+)\s*\n"
    )

    def execute_cli(self):
        v = self.cli("show version", cached=True)
        match = self.rx_mac_search.search(v)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac"),
        }
