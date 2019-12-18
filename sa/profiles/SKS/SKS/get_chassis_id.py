# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# SKS.SKS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "SKS.SKS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^(?:System|Base ethernet) MAC Address:\s+(?P<mac>\S+)", re.MULTILINE)
    rx_cpu_mac = re.compile(r"^(?P<mac>(?:[0-9a-f]{2}:){5}[0-9a-f]{2})", re.MULTILINE)

    def execute_cli(self):
        try:
            c = self.cli("show system", cached=True)
        except self.CLISyntaxError:
            c = self.cli("show version", cached=True)
        match = self.rx_mac.search(c)
        if not match:
            try:
                c = self.cli("show system unit 1 ", cached=True)
                match = self.rx_mac.search(c)
            except self.CLISyntaxError:
                c = self.cli("show mac-address cpu", cached=True)
                match = self.rx_cpu_mac.search(c)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
