# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## Extreme.XOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2015 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
import re
## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP

rx_line = re.compile(
    r"^\S+\s+(?P<ip>\d+\S+)\s+(?P<mac>\S+)\s+\d+\s+\S+\s+(?P<interface>\S+).+$")


class Script(BaseScript):
    name = "Extreme.XOS.get_arp"
    interface = IGetARP

    def execute(self):
        return self.cli("sh iparp", list_re=rx_line)
