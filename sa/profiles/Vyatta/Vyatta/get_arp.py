# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Vyatta.Vyatta.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2010 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP
##
## Vyatta.Vyatta.get_arp
##
class Script(NOCScript):
    name="Vyatta.Vyatta.get_arp"
    implements=[IGetARP]
    
    rx_line=re.compile(r"^(?P<ip>\d+\.\d+\.\d+\.\d+)\s+\S+\s+(?P<mac>[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2}:[0-9a-f]{2})\s+\S+\s+(?P<interfae>\S+)$")
    def execute(self):
        return self.cli("show arp", list_re=self.rx_line)
    

