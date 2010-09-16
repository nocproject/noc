# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Juniper.JUNOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2009 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
import noc.sa.script
from noc.sa.interfaces import IGetARP
import re

rx_line=re.compile(r"^(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+(?P<ip>\d+\.\d+\.\d+\.\d+)\s+(?P<interface>\S+)")

class Script(noc.sa.script.Script):
    name="Juniper.JUNOS.get_arp"
    implements=[IGetARP]
    def execute(self):
        return self.cli("show arp no-resolve",list_re=rx_line)
