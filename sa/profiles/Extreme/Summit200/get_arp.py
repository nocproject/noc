# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Extreme.Summit200.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP


class Script(BaseScript):
    name = "Extreme.Summit200.get_arp"
    interface = IGetARP
    rx_line = re.compile(
        r"^(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+\d+\s+\S+\s+(?P<interface>\S+)\s+",
        re.MULTILINE,
    )

    def execute_cli(self):
        return self.cli("show iparp", list_re=self.rx_line)
