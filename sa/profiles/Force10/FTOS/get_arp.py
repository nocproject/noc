# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line = re.compile(
    r"^Internet\s+(?P<ip>\S+)\s+\d+\s+(?P<mac>\S+)\s+(?P<interface>\S+\s+\S+)")


class Script(noc.sa.script.Script):
    name = "Force10.FTOS.get_arp"
    implements = [IGetARP]

    def execute(self):
        return self.cli("show arp", list_re=rx_line)
