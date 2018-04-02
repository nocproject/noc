# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# IBM.NOS.get_chassis_id
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
    name = "IBM.NOS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    #
    # IBM Flex System Ethernet I/O modules
    # Single chassis mac
    #
    rx_small = re.compile(
        r"^MAC address\:\s+(?P<mac>\S+)",
        re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show version")
        match = self.rx_small.search(v)
        base = match.group("mac")
        return [{
            "first_chassis_mac": base,
            "last_chassis_mac": base
        }]
