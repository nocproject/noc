# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Juniper.JUNOSe.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2016 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re
# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP

class Script(BaseScript):
    name = "Juniper.JUNOSe.get_arp"
    interface = IGetARP

    rx_line = re.compile(
        r"^\s*(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\d+\s+"
        r"(?P<mac>[0-9a-f]{4}\.[0-9a-f]{4}\.[0-9a-f]{4})\s+"
        r"(?P<interface>\S+)")

    def execute(self):
        return self.cli("show arp", list_re=self.rx_line)
