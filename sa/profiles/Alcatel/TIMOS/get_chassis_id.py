# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Alcatel.TIMOS.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alcatel.TIMOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(r"^\s*Base MAC address\s*:\s*(?P<id>\S+)",
                       re.IGNORECASE | re.MULTILINE)

    def execute(self):
        r = []
        v = self.cli("show chassis")
        match = self.re_search(self.rx_id, v)
        r += [{
            "first_chassis_mac": match.group("id"),
            "last_chassis_mac": match.group("id")
        }]
        try:
            v = self.cli("show card detail")
            for match in self.rx_id.finditer(v):
                r += [{
                    "first_chassis_mac": match.group("id"),
                    "last_chassis_mac": match.group("id")
                }]
        except self.CLISyntaxError:
            pass
        return r
