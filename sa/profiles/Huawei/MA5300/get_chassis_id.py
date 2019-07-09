# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Huawei.MA5300.get_chassis_id
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
    name = "Huawei.MA5300.get_chassis_id"
    reuse_cli_session = False
    interface = IGetChassisID

    rx_mac = re.compile(
        r"^\s*The bridge has priority \d+, MAC address:\s+(?P<mac>\S+)", re.MULTILINE
    )

    def execute(self):
        v = self.cli("show spanning-tree")
        match = self.rx_mac.search(v)
        return {"first_chassis_mac": match.group("mac"), "last_chassis_mac": match.group("mac")}
