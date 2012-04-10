# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2012 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.sa.script import Script as NOCScript
from noc.sa.interfaces import IGetARP

rx_line = re.compile(
    r"^(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+\S+\s+\S+\s+(?P<interface>\S+)\(.+$")


class Script(NOCScript):
    name = "Extreme.XOS.get_arp"
    implements = [IGetARP]

    def execute(self):
        return self.cli("sh iparp", list_re=rx_line)
