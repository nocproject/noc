# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.ProCurve.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line = re.compile(r"^\s*(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<mac>[0-9a-f]{6}-[0-9a-f]{6})\s+(?:dynamic|static)\s+(?P<interface>\S+)")


class Script(noc.sa.script.Script):
    name = "HP.ProCurve.get_arp"
    implements = [IGetARP]

    def execute(self):
        return self.cli("show arp", list_re=rx_line)
