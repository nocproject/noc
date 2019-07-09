# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# ZTE.ZXA10.get_arp
# ---------------------------------------------------------------------
# Copyright (C) 2007-2019 The NOC Project
# See LICENSE for details
# ---------------------------------------------------------------------

# Python modules
import re

# NOC modules
from noc.sa.interfaces.igetarp import IGetARP
from noc.core.script.base import BaseScript


class Script(BaseScript):
    name = "ZTE.ZXA10.get_arp"
    interface = IGetARP

    rx_arp = re.compile(
        r"^(?P<ip>\S+)\s+(?:\d+|\-)\s+(?P<mac>[0-9a-f\.]+)\s+(?P<interface>\S+)", re.MULTILINE
    )

    def execute_cli(self):
        v = self.cli("show arp")
        return [match.groupdict() for match in self.rx_arp.finditer(v)]
