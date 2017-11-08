# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zyxel.DSLAM.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Zyxel.DSLAM.get_chassis_id"
    interface = IGetChassisID

    rx_mac1 = re.compile(
        r"^\s*\S+ mac\s*: (?P<mac>\S+)\s*\n", re.MULTILINE)
    rx_mac2 = re.compile(
        r"^\s*mac address\s*: (?P<mac>\S+)\s*\n", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        r = []
        for i in range(1, 19):
            try:
                v = self.cli("lcman show %s" % i)
                for match in self.rx_mac1.finditer(v):
                    r += [{
                        "first_chassis_mac": match.group("mac"),
                        "last_chassis_mac": match.group("mac")
                    }]
                for match in self.rx_mac2.finditer(v):
                    r += [{
                        "first_chassis_mac": match.group("mac"),
                        "last_chassis_mac": match.group("mac")
                    }]
            except self.CLISyntaxError:
                break
        if not r:
            match = self.rx_mac2.search(self.cli("sys info show"))
            return [{
                "first_chassis_mac": match.group("mac"),
                "last_chassis_mac": match.group("mac")
            }]
        return r
