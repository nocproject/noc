# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Alstec.24xx.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.snmp.error import SNMPError


class Script(BaseScript):
    name = "Alstec.24xx.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^\s*(MAC Address|Burned In MAC Address)\s*\.+ (?P<mac>\S+)\s*.+", re.MULTILINE
    )

    def execute_snmp(self, **kwargs):
        try:
            mac = self.snmp.get("1.3.6.1.4.1.27142.1.1.1.1.1.9.0")
            return {"first_chassis_mac": mac, "last_chassis_mac": mac}
        except SNMPError:
            raise NotImplementedError

    def execute_cli(self, **kwargs):
        match = self.rx_mac.search(self.cli("show network", cached=True))
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
