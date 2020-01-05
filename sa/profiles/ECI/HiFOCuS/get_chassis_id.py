# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.HiFOCuS.get_chassis_id
# ---------------------------------------------------------------------
# Copyright (C) 2007-2017 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.profiles.Generic.get_chassis_id import Script as BaseScript
from noc.sa.interfaces.igetchassisid import IGetChassisID


class Script(BaseScript):
    name = "ECI.HiFOCuS.get_chassis_id"
    interface = IGetChassisID
    reuse_cli_session = False
    keep_cli_session = False
    cache = True
    always_prefer = "S"

    rx_mac1 = re.compile(
        r"^\s*OUTBAND\s+\|\s(?P<mac1>\S+)\n\s*INBAND\s+\|\s(?P<mac2>\S+)$", re.MULTILINE
    )
    rx_mac2 = re.compile(r"^\s*(?:[\S ]+)\s+\s(?P<mac>\S+)$", re.MULTILINE)

    def execute_cli(self, **kwargs):
        cmd = self.cli("MACREAD")
        match = self.rx_mac1.search(cmd)
        if match:
            fmac = match.group("mac1")
            lmac = match.group("mac2")
        else:
            match = self.rx_mac2.search(cmd)
            fmac = match.group("mac")
            lmac = fmac
        return [{"first_chassis_mac": fmac, "last_chassis_mac": lmac}]
