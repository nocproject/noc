# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# Juniper.EX2500.get_chassis_id
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "Juniper.EX2500.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac = re.compile(
        r"^MAC Address:\s+(?P<mac1>\S+).*"
        r"^Management Port MAC Address:\s+(?P<mac2>\S+)",
        re.MULTILINE | re.DOTALL)

    def execute(self):
        v = self.cli("show sys-info", cached=True)
        match = self.rx_mac.search(v)
        return {
            "first_chassis_mac": match.group("mac1"),
            "last_chassis_mac": match.group("mac2")
        }
