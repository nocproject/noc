# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Force10.FTOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re

rx_line = re.compile(
    r"^Internet\s+(?P<ip>\S+)\s+\d+\s+(?P<mac>\S+)\s+(?P<interface>\S+\s+\S+)")


class Script(BaseScript):
    name = "Force10.FTOS.get_arp"
    interface = IGetARP

    def execute(self):
        return self.cli("show arp", list_re=rx_line)
