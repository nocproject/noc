# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.5440.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
import re

from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Alstec.5440.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^\s+\d+\s+([0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:"
        r"[0-9a-f]{2}:[0-9a-f]{2})\s+yes",
        re.MULTILINE)

    def execute(self):
        v = self.cli("brctl showmacs br0", cached=True)
        macs = self.rx_mac.findall(v)
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
