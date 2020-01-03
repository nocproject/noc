# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DLink.DAS.get_chassis_id
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
    name = "DLink.DAS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^\d+\s+\| ([0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2}:[0-9A-F]{2})",
        re.MULTILINE,
    )

    def execute_cli(self, **kwargs):
        macs = sorted(self.rx_mac.findall(self.cli("get system manuf info", cached=True)))
        return [
            {"first_chassis_mac": f, "last_chassis_mac": t} for f, t in self.macs_to_ranges(macs)
        ]
