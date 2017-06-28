# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.MXK.get_chassis_id
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
    name = "Zhone.MXK.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_line = re.compile(
        r"^\S+\s+UP\s+\d+\s+\S+\s+(?P<mac>\S+)\s+\S+", re.MULTILINE)

    def execute(self):
        v = self.cli("interface show", cached=True)
        macs = self.rx_line.findall(v)
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
