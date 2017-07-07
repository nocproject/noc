# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ECI.SAM.get_chassis_id
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
    name = "ECI.SAM.get_chassis_id"
    interface = IGetChassisID
    cache = True

    rx_mac1 = re.compile(r"^\s*OUTBAND\s+\|\s(?P<mac>\S+)$", re.MULTILINE)
    rx_mac2 = re.compile(r"^\s*INBAND\s+\|\s(?P<mac>\S+)$", re.MULTILINE)

    def execute(self):
        with self.profile.shell(self):
            self.cli("SHELF")
            self.cli("EEPROM")
            cmd = self.cli("MACREAD")
            match1 = self.rx_mac1.search(cmd)
            if match1:
                mac1 = match1.group("mac")
            match2 = self.rx_mac2.search(cmd)
            if match2:
                mac2 = match2.group("mac")
        return [{
            "first_chassis_mac": mac1,
            "last_chassis_mac": mac2
        }]
