# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NSCComm.LPOS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "NSCComm.LPOS.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(r"^Physical Address\s+: (?P<mac>\S+)", re.MULTILINE)


    def execute(self):
        match = self.rx_mac.search(self.cli("stats", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
