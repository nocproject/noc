# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Eltex.LTE.get_chassis_id
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
    name = "Eltex.LTE.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac1 = re.compile(r"MAC address:\s*\n^\s+(?P<mac>\S+)", re.MULTILINE)
    rx_mac2 = re.compile(r"^Port \d+ MAC address: (?P<mac>\S+)", re.MULTILINE)

    def execute(self):
        macs = []
        with self.profile.switch(self):
            cmd = self.cli("show version")
            match = self.rx_mac1.search(cmd)
            if match:
                macs += [match.group("mac")]
            cmd = self.cli("show interfaces mac-address")
            macs += self.rx_mac2.findall(cmd)
        if not macs:
            mac_table = self.scripts.get_mac_address_table()
            for m in mac_table:
                if m["type"] == "C":
                    macs += [m["mac"]]
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
