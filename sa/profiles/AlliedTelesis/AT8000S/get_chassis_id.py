# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# AlliedTelesis.AT8000S.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.lib.text import parse_table
import re


class Script(BaseScript):
    name = "AlliedTelesis.AT8000S.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^System MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        macs = []
        match = self.re_search(self.rx_mac, self.cli("show system"))
        mac = match.group("mac")

        try:
            v = self.cli("show stack", cached=True)
            for i in parse_table(v, footer="Topology is "):
                for m in macs:
                    if m == i[1]:
                        break
                else:
                    macs += [i[1]]
        except self.CLISyntaxError:
            pass

        if macs:
            macs.sort()
            return [{
                "first_chassis_mac": f,
                "last_chassis_mac": t
            } for f, t in self.macs_to_ranges(macs)]

        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
