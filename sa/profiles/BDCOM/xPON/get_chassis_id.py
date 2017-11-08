# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# BDCOM.xPON.get_chassis_id
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
    name = "BDCOM.xPON.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^All\s+(?P<mac>\S+)",
        re.MULTILINE)

    # @todo: cli g0/* - *

    def execute(self):
        if self.has_snmp():
            try:
                macs = []
                for v in self.snmp.get_tables(
                        ["1.3.6.1.2.1.2.2.1.6"], bulk=True):
                    macs += [v[1]]
                return {
                    "first_chassis_mac": min(macs),
                    "last_chassis_mac": max(macs)
                }
            except self.snmp.TimeOutError:
                pass
        match = self.rx_mac.search(self.cli("show mac address-table static", cached=True))
        mac = match.group("mac")
        return {
            "first_chassis_mac": mac,
            "last_chassis_mac": mac
        }
