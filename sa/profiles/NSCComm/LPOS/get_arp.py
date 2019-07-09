# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------
# NSCComm.LPOS.get_arp
# ----------------------------------------------------------------------
# Copyright (C) 2007-2018 The NOC Project
# See LICENSE for details
# ----------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "NSCComm.LPOS.get_arp"
    interface = IGetARP
    cache = True

    rx_line = re.compile(
        r"^\s*(?P<interface>\d+)\s+(?P<ip>\d+\S+\d+)\s+(?P<mac>\S+)\s+\d+\s*\n", re.MULTILINE
    )

    def execute(self):
        r = []
        v = self.cli("arp")
        for match in self.rx_line.finditer(v):
            r += [match.groupdict()]
        return r
