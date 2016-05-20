# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## DLink.DxS.get_chassis_id
##----------------------------------------------------------------------
## Copyright (C) 2007-2016 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
import re


class Script(BaseScript):
    name = "DLink.DxS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_ver = re.compile(r"^MAC Address\s+:\s*(?P<id>\S+)",
        re.IGNORECASE | re.MULTILINE)
    rx_line = re.compile(
        r"^\s*\d+\s+(?:\S+\s+)?"
        r"([0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-[0-9A-F]{2}-"
        r"[0-9A-F]{2}-[0-9A-F]{2})\s+CPU\s+Self\s*(?:\S*\s*)?$",
        re.MULTILINE)

    def execute(self):
        try:
            v = self.cli("show fdb static", cached=True)
            macs = self.rx_line.findall(v)
            if macs:
                macs.sort()
                return [{
                    "first_chassis_mac": f,
                    "last_chassis_mac": t
                } for f, t in self.macs_to_ranges(macs)]
        except:
            pass

        match = self.re_search(self.rx_ver, self.cli("show switch",
            cached=True))
        mac = match.group("id")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
