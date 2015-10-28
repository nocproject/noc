# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
# Force10.SFTOS.get_arp
##----------------------------------------------------------------------
## Copyright (C) 2007-2013 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## NOC modules
from noc.core.script.base import BaseScript
from noc.sa.interfaces.igetarp import IGetARP
from noc.lib.text import parse_table


class Script(BaseScript):
    name = "Force10.SFTOS.get_arp"
    interface = IGetARP

    def execute(self):
        return [{
            "ip": x[0],
            "mac": x[1],
            "interface": x[2]
        } for x in parse_table(self.cli("show arp"))]
