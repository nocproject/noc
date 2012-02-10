# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## f5.BIGIP.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------
"""
"""
## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP


class Script(NOCScript):
    name = "f5.BIGIP.get_arp"
    implements = [IGetARP]

    rx_line = re.compile(r"^ARP\s+(?P<ip>\S+)\s+-\s+(?P<mac>\S+)\s+VLAN\s+(?P<interface>.+?)\s+expire")

    def execute(self):
        return self.cli("b arp show | grep -v '(incomplete)'",
                        list_re=self.rx_line)
