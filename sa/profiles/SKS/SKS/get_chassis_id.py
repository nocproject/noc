# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------


from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "SKS.SKS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^(?:System|Base ethernet) MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        try:
            c = self.cli("show system", cached=True)
        except self.CLISyntaxError:
            c = self.cli("show version", cached=True)
        match = self.rx_mac.search(c)
        if not match:
            c = self.cli("show system unit 1 ", cached=True)
            match = self.rx_mac.search(c)
        return {
            "first_chassis_mac": match.group("mac"),
            "last_chassis_mac": match.group("mac")
        }
