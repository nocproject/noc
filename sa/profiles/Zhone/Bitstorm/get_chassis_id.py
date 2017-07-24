# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Zhone.Bitstorm.get_chassis_id
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
    name = "Zhone.Bitstorm.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_ver = re.compile(
        r"^FW Rev\s*(?P<version>\S+)\n"
        r"^Model\s*(?P<platform>\S+)\n"
        r"^Serial Number\s*(?P<serial>\S+)\n"
        r"^MAC Address Eth1\s*(?P<mac1>\S+)\n"
        r"^MAC Address Eth2\s*(?P<mac2>\S+)\n", re.MULTILINE | re.IGNORECASE)

    def execute(self):
        v = self.cli("show system information", cached=True)
        match = self.rx_ver.search(v)
        if match:
            return {
                "first_chassis_mac": match.group("mac1"),
                "last_chassis_mac": match.group("mac2")
            }
        else:
            return {}
