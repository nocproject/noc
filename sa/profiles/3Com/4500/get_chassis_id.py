# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# 3Com.4500.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID
from noc.core.comp import smart_text


class Script(BaseScript):
    name = "3Com.4500.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^\s+First mac address\s+:\s+(?P<mac>\S+)$", re.MULTILINE)

    def execute_snmp(self):
        macs = []
        for v in self.snmp.get_tables(["1.3.6.1.2.1.2.2.1.6"]):
            macs += [v[1]]
        macs = [x for x in macs if x != smart_text("\x00\x00\x00\x00\x00\x00")]
        return {"first_chassis_mac": min(macs), "last_chassis_mac": max(macs)}

    def execute_cli(self):
        v = self.cli("display device manuinfo", cached=True)
        match = self.rx_mac.search(v)
        mac = match.group("mac")
        return {"first_chassis_mac": mac, "last_chassis_mac": mac}
