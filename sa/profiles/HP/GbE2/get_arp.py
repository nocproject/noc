# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## HP.GbE2.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
import re

rx_line = re.compile(r"^\s*(?P<ip>\d+\.\d+\.\d+\.\d+).+?(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+\d+\s+(?P<interface>\S+)")


class Script(BaseScript):
    name = "HP.GbE2.get_arp"
    interface = IGetARP

    def execute(self):
        r = self.cli("/i/l3/arp/dump", list_re=rx_line)
        self.cli("/")
        return r
