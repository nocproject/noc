# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# DCN.DCWS.get_chassis_id
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
    name = "DCN.DCWS.get_chassis_id"
    cache = True
    interface = IGetChassisID

    rx_first = re.compile(r"^\s*CPU\s+MAC\s+(?P<fmac>\S+)\n", re.MULTILINE)
    rx_last = re.compile(r"^\s*VLAN\s+MAC\s+(?P<lmac>\S+)\n", re.MULTILINE)

    def execute(self):
        ver = self.cli("show version", cached=True)
        fmatch = self.re_search(self.rx_first, ver)
        lmatch = self.re_search(self.rx_last, ver)
        return [{
            "first_chassis_mac": fmatch.group("fmac"),
            "last_chassis_mac": lmatch.group("lmac")
        }]
