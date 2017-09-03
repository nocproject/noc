# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# NAG.SNR.get_chassis_id
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
    name = "NAG.SNR.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^\s+\S+\s+mac\s+(\S+)\s*\n", re.MULTILINE | re.IGNORECASE
    )

    def execute(self):
        # Try SNMP first
        if self.has_snmp():
            try:
                mac = self.snmp.get("1.3.6.1.2.1.2.2.1.6.1", cached=True)
                return {
                    "first_chassis_mac": mac,
                    "last_chassis_mac": mac
                }
            except self.snmp.TimeOutError:
                pass

        # Fallback to CLI
        macs = self.rx_mac.findall(self.cli("show version", cached=True))
        macs.sort()
        return [{
            "first_chassis_mac": f,
            "last_chassis_mac": t
        } for f, t in self.macs_to_ranges(macs)]
