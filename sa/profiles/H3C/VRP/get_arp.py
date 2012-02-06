# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## H3C.VRP.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.interfaces import IGetARP
from noc.sa.script import Script as NOCScript


class Script(NOCScript):
    name = "H3C.VRP.get_arp"
    implements = [IGetARP]

    rx_arp_line = re.compile(r"^(?P<ip>\d+\.\S+)\s+(?P<mac>[0-9a-f]\S+)\s+\d*\s+.{3}\s+(?P<interface>\S+)", re.IGNORECASE | re.DOTALL | re.MULTILINE)

    def execute(self):
        return self.cli("display arp", list_re=self.rx_arp_line)
