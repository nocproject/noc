# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5600T.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "Huawei.MA5600T.get_chassis_id"
    interface = IGetChassisID
    rx_mac = re.compile(
        r"^\s*Current MAC address of active (?:main|control )board:\s+(?P<mac>\S+)",
        re.MULTILINE)

    def execute(self):
        match = self.re_search(self.rx_mac,
            self.cli("display sysman mac-address"))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
