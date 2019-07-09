# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Vector.Lambda.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Vector.Lambda.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_mac = re.compile(r"^MAC\s+addr\s+:\s+(?P<mac>\S+)", re.MULTILINE)

    def execute_cli(self, **kwargs):
        cmd = self.cli("net dump")
        match = self.rx_mac.search(cmd)
        if match:
            mac = match.group("mac")
        else:
            raise self.NotSupportedError
        return [{"first_chassis_mac": mac, "last_chassis_mac": mac}]
