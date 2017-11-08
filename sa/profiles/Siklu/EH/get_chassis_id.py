# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Siklu.EH.get_chassis_id
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
    name = "Siklu.EH.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_id = re.compile(
        r"^eth \S+ mac-addr\s+:\s*(\S+)\s*$",
        re.IGNORECASE | re.MULTILINE
    )

    def execute(self):
        v = self.cli("show eth all")
        macs = self.rx_id.findall(v)
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
